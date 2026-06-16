# Chrome CDP 永久 TCP 中继

## 问题

用户 Windows Chrome 用 `--remote-debugging-port=9222` 启动，但端口绑定在 `127.0.0.1`（仅 Windows 本地可访问）。WSL 无法直连 Windows 的 `127.0.0.1`。

## 永久方案（2026-06-09，已验证有效）

两层中继：

```
Chrome (127.0.0.1:9222)
  ↕  C# 中继 Relay2.exe 在 Windows 跑 (0.0.0.0:9255 → 127.0.0.1:9222)
Windows IP 172.24.48.x:9255  (从 WSL 可达)
  ↕  Python 中继 chrome_relay.py 在 WSL 跑 (localhost:19223 → GW:9255)
Playwright connect_over_cdp('http://localhost:19223')
```

## C# 中继编译命令

```powershell
Add-Type -Language CSharp -TypeDefinition @"
using System;
using System.Net;
using System.Net.Sockets;
using System.Threading.Tasks;
public class Relay {
    public static void Main() {
        var listener = new TcpListener(IPAddress.Any, 9255);
        listener.Start();
        Console.WriteLine("Relay running");
        while (true) {
            var c = listener.AcceptTcpClient();
            Task.Run(async () => {
                using(c) try {
                    using(var r = new TcpClient()) {
                        await r.ConnectAsync("127.0.0.1", 9222);
                        var s1 = c.GetStream();
                        var s2 = r.GetStream();
                        await Task.WhenAll(s1.CopyToAsync(s2), s2.CopyToAsync(s1));
                    }
                } catch {}
            });
        }
    }
}
"@ -OutputAssembly "C:\Users\[你的Windows用户名]\AppData\Local\Relay2.exe" -OutputType ConsoleApplication
```

⚠️ `CopyToAsync` + `Task.WhenAll` 是关键——用 async 非阻塞双向转发，否则单向 CopyTo 阻塞挂死。

## WSL Python 中继

保存在 `~/.hermes/scripts/chrome_relay.py`。自动检测网关 IP。

```python
GW = os.popen("ip route | grep default | awk '{print $3}''").read().strip()
# 连接 GW:9255 (Windows 上 C# relay), 监听 localhost:19223
```

## Hermes 配置直连

### ✅ 实际验证有效的配置（2026-06-22 更新）

实际工作链是 WSL relay 监听 `127.0.0.1:19223` 并转发到 `GW:9255`：
```
Playwright/CDP → ws://127.0.0.1:19223 → WSL relay → Windows:9255 → Relay2 → Chrome:9222
```

```bash
# 1. 从 WSL relay 获取 WebSocket URL（127.0.0.1:19223，不是 172.24.48.1:9255）
CDP_URL=$(curl -s http://127.0.0.1:19223/json/version | \
  python3 -c "import json,sys; print(json.load(sys.stdin)['webSocketDebuggerUrl'])")

# 2. 写入 Hermes 配置
hermes config set browser.cdp_url "$CDP_URL"

# 3. 验证
hermes config get browser.cdp_url
# → ws://127.0.0.1:19223/devtools/browser/<uuid>
```

### ⚠️ 要点

1. **不能用 `/auto`** — TCP relay 不处理 Chrome DevTools 的 `/auto` WebSocket 自动发现。必须用具体 browser UUID。
2. **每次 Chrome 重启 UUID 会变** — 如果 browser_navigate 报 404，重新执行上述 curl 命令获取新 UUID。
3. **Playwright 用 HTTP URL：** `connect_over_cdp('http://127.0.0.1:19223')` 而非 WebSocket URL。Playwright 内部会自动发现 WebSocket 端点。
4. **Hermes browser 工具用 WebSocket URL** — `ws://127.0.0.1:19223/devtools/browser/<uuid>`（配置在 config.yaml 的 `browser.cdp_url`）。

### 从 WSL 启动 Chrome 的正确步骤（2026-06-22 新增）

1. 先杀所有旧 Chrome 进程：
   ```bash
   cmd.exe /c "taskkill /F /IM chrome.exe" 2>/dev/null
   ```
2. 切到 Windows 盘（避免 UNC 路径错误）：
   ```bash
   cd /mnt/c/Users/[你的Windows用户名]
   ```
3. 启动带调试端口的 Chrome：
   ```bash
   cmd.exe /c "start /B chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\Users\[你的Windows用户名]\Desktop\chrome-debug --no-first-run --no-default-browser-check https://www.dianxiaomi.com/index.htm"
   ```
4. 等待 5-8 秒让 Chrome 启动
5. 验证 CDP 在线：
   ```bash
   curl -s http://127.0.0.1:19223/json/version
   ```
6. 更新 Hermes config browser.cdp_url（如果 UUID 变了）

### ❌ 旧方法（不再使用）

以下方法曾被写入但实际验证不可靠，保留仅作记录：

- `ws://172.24.48.1:9255/devtools/browser/<id>` — 绕过 WSL relay 直连 Windows:9255，但 Hermes config 走此路径时 browser_navigate 不稳定
- `ws://127.0.0.1:19223/devtools/browser/auto` — 经 TCP relay 时 `/auto` 返回 404

## 检测中继

```bash
# 通过完整中继链测试
curl -s --max-time 3 http://localhost:19223/json/version
# 返回 Chrome DevTools JSON → 在线
# 超时/空 → 中继挂了

# 分段检测
# 1. WSL 中继本身是否在监听
curl -s --max-time 3 http://localhost:19223/ 2>&1 | head -3
# 2. Windows C# relay 是否可达
curl -s --max-time 3 http://172.24.48.1:9255/ 2>&1 | head -3
# 3. Chrome 调试端口是否在监听
powershell.exe -Command "netstat -ano | Select-String '9222'"
# 4. Chrome 进程是否存在
powershell.exe -Command "Get-Process chrome -ErrorAction SilentlyContinue | Measure-Object | Select-Object Count"
```

### ⚡ 快速检修脚本（从 WSL 执行，2026-06-22 新增）

当 CDP 不通时，按顺序执行以下步骤：

```bash
# 1. 先杀全部 Chrome（可能堆积了多个孤儿进程）
cmd.exe /c "taskkill /F /IM chrome.exe" 2>/dev/null
sleep 3

# 2. 确认 9222 空闲
cmd.exe /c "netstat -ano | findstr LISTENING | findstr 9222" 2>/dev/null && echo "Port 9222 still in use!" && exit 1

# 3. 切到 Windows 盘（⚠️ 避免 UNC path not supported 错误）
cd /mnt/c/Users/[你的Windows用户名] || cd /mnt/c/

# 4. 启动带调试端口的 Chrome
cmd.exe /c "start /B chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\Users\[你的Windows用户名]\Desktop\chrome-debug --no-first-run --no-default-browser-check" 2>&1
sleep 8

# 5. 验证 CDP 链
timeout 5 curl -s http://127.0.0.1:19223/json/version 2>&1 | head -5

# 6. 更新 Hermes config（如果 UUID 变了）
CDP_URL=$(curl -s http://127.0.0.1:19223/json/version | python3 -c "import json,sys; print(json.load(sys.stdin)['webSocketDebuggerUrl'])")
hermes config set browser.cdp_url "$CDP_URL"
```

## ⚠️ 已验证失败的端口转发方案（2026-06-11）

### `netsh interface portproxy`

```
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=19223 connectaddress=127.0.0.1 connectport=19223
```

**现象：** TCP 连接能建立（`ESTABLISHED`），甚至能从 netstat 看到双向连接。但 HTTP 请求无响应（0 字节），WebSocket 握手超时。

**原因推测：** Windows portproxy (NAT 驱动) 在 Hyper-V / WSL2 虚拟网络环境中，不能正确处理 Chrome DevTools Protocol 的 WebSocket 升级握手和双向数据流。HTTP 响应在返回路径上丢失。

**结论：❌ 不可用。** 无论 HTTP GET、WebSocket upgrade、还是原始 TCP 数据，都无法通过 portproxy 与 Chrome DevTools 通信。C# `TcpListener` 中继（Relay2.exe）是唯一有效方案。

### PowerShell 纯 TCP 中继

```powershell
$l = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Any, 19223)
$l.Start()
```

**现象：** 从 WSL 通过 `powershell.exe -Command` 调用时，PowerShell 变量 `$_.Id` 被 bash 展开破坏。单层 `ScriptBlock` 中的 `TcpClient` 连接 `127.0.0.1:19223` 成功但 `GetStream()` 返回 null。

**结论：❌ 不可用。** 从 WSL 调用 Windows PowerShell 的变量转义问题不可绕过。必须用 .ps1 文件 + `-File` 参数执行完整脚本。但即使如此，TCP 中继的稳定性不如 C# Relay2.exe。

### 直接 `chrome.exe --remote-debugging-port=9222` 启动失败

**现象：** Chrome 打开但无黄色调试提示条，curl 无响应。
**原因：** 已有 Chrome 进程未完全关闭。Windows Chrome 的进程模型导致子进程之间存在继承关系，新实例的调试端口被忽略。
**修复：** 必须用 `Stop-Process -Force` 杀掉所有 chrome.exe，确认 `Get-Process chrome` 返回 0，再启动。

## VBS 开机自启

文件：`C:\Users\[你的Windows用户名]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hermes-chrome-relay.vbs`

```vbscript
' Start Windows C# relay
WshShell.Run "C:\Users\[你的Windows用户名]\AppData\Local\Relay2.exe", 0, False
' Start WSL (triggers systemd boot)
WshShell.Run "wsl.exe -d Ubuntu-24.04", 0, False
' Wait 5s for WSL boot, then start Python relay
WScript.Sleep 5000
WshShell.Run "wsl.exe -d Ubuntu-24.04 -e python3 /home/xiaoyao/.hermes/scripts/chrome_relay.py", 0, False
```

## ⚠️ browser_navigate/snapshot auto-launch 失败（2026-06-14 新增）

**现象：** CDP 中继链正常（`curl http://127.0.0.1:19223/json/version` 返回 200），`browser_cdp` 工具可以正常发送 CDP 命令（`Target.getTargets`, `Runtime.evaluate`, `Page.navigate`, `Page.captureScreenshot` 等全部正常），但 `browser_navigate`、`browser_snapshot`、`browser_console`、`browser_click` 等 Hermes 封装工具全部报 `Auto-launch failed: CDP WebSocket connect failed: HTTP error: 404 Not Found`。

**原因：** Hermes 的 `browser_navigate` 等工具内部有 auto-launch 机制，尝试用不同于 `browser_cdp` 的方式建立 CDP 连接，经过 TCP relay 时 WebSocket 握手失败返回 404。`browser.engine` 设为 `cdp` 或 `auto` 均无法绕过。

**已验证失败的操作：**
- 设置 `browser.engine = cdp` → 仍报 auto-launch 404
- 设置 `browser.cdp_url = http://127.0.0.1:19223` → 仍报 auto-launch 404
- 设置 `browser.cdp_url = ws://127.0.0.1:19223/devtools/browser/<uuid>` → 仍报 auto-launch 404

**当前可用方案：** 全部通过 `browser_cdp` 工具操作，绕过 auto-launch：
- 导航：`browser_cdp(method='Page.navigate', params={'url': '...'}, target_id='...')`
- 截图：`browser_cdp(method='Page.captureScreenshot', params={'format':'png'}, target_id='...')`
- 执行 JS：`browser_cdp(method='Runtime.evaluate', params={'expression':'...', 'returnByValue':true}, target_id='...')`
- 获取标签页列表：`browser_cdp(method='Target.getTargets', params={})`
- target_id 从 `Target.getTargets` 返回的 `targetInfos[].targetId` 获取

**后续：** 此问题可能随 Hermes 版本更新修复。每次会话先尝试 `browser_navigate`，若仍报 auto-launch 404 则回退到 `browser_cdp` 方案。不要硬编码"browser_navigate 永远不可用"的结论。

## 中继重建

如果 `Relay2.exe` 被误删或需要重新编译：

```powershell
Add-Type -Language CSharp -TypeDefinition "@ ...
"@ -OutputAssembly "C:\Users\[你的Windows用户名]\AppData\Local\Relay2.exe" -OutputType ConsoleApplication
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*