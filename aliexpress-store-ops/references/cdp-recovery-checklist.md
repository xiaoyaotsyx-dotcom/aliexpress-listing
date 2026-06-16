# CDP 断线恢复检查清单

当 CDP 连接中断、browser 工具 404/超时时，按此清单逐项排查。
**不要从头重现试错过程**——此清单压缩了 3 次断线恢复的经验。

---

## 1. 快速诊断（30秒）

```bash
# ① WSL relay 是否在监听？
ss -tlnp | grep 19223

# ② Relay2.exe 是否在 Windows 上运行？
powershell.exe -Command "Get-Process -Name 'Relay2' -ErrorAction SilentlyContinue | Select-Object Id"

# ③ Chrome 调试端口 9222 是否绑定？
powershell.exe -Command "netstat -ano | findstr ':9222' | findstr LISTENING"

# ④ CDP API 是否可访问？
curl -s --max-time 5 http://127.0.0.1:19223/json/version | head -5
```

## 2. 分层恢复

### 情况 A：Chrome 9222 不在了（最常见）

```bash
# 杀干净所有 Windows Chrome
cmd.exe /c "taskkill /F /IM chrome.exe" 2>/dev/null; sleep 3

# 启动带调试端口的 Chrome（PowerShell 方式 — 2026-07-18 验证有效）
/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -Command "Start-Process 'C:\Program Files\Google\Chrome\Application\chrome.exe' -ArgumentList '--remote-debugging-port=9222', '--user-data-dir=C:\Users\[你的Windows用户名]\Desktop\chrome-debug'"
sleep 8

# 启动 WSL relay
# 使用 terminal(background=true) 启动
python3 /home/xiaoyao/.hermes/scripts/chrome_relay.py
sleep 3

# 验证全链路
curl -s http://127.0.0.1:19223/json/version | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('Browser','FAIL'))"
```

**如果上述失败（Cmd start 不绑定端口）：**
```bash
# VBS 启动（备用），需先在桌面创建 start_debug_chrome.vbs
cd /mnt/c/Users/[你的Windows用户名] && cmd.exe /c "wscript.exe C:\Users\[你的Windows用户名]\Desktop\start_debug_chrome.vbs"
sleep 5
```

### 情况 B：Chrome 在跑但 Relay2 不在了

```bash
# Windows 上先杀旧 Relay2
powershell.exe -Command "Get-Process Relay2 -ErrorAction SilentlyContinue | Stop-Process -Force"
sleep 1

# 启动新 Relay2（路径按实际情况）
# 通常在 C:\Users\[你的Windows用户名]\relay-tunnel\Relay2.exe 或启动项中
powershell.exe -Command "Start-Process -FilePath 'C:\Users\[你的Windows用户名]\relay-tunnel\Relay2.exe'"
sleep 3

# 验证
powershell.exe -Command "netstat -ano | findstr ':9255' | findstr LISTENING"
```

### 情况 C：WSL relay 挂了（19223 不监听）

```bash
# 后台启动 chrome_relay.py
# 用 background=true
python3 /home/xiaoyao/.hermes/scripts/chrome_relay.py
# 验证
sleep 1
ss -tlnp | grep 19223
```

### 情况 D：全部在线但 browser_cdp 404

浏览器 ID 变了，需要更新 Hermes config：

```bash
# 获取新 WebSocket URL
BROWSER_WS=$(curl -s http://127.0.0.1:19223/json/version | python3 -c "import json,sys; print(json.load(sys.stdin)['webSocketDebuggerUrl'])")
echo "New WS: $BROWSER_WS"

# 更新 Hermes config（必须用 hermes config set，不能用 patch/write_file）
hermes config set browser.cdp_url "$BROWSER_WS"

# 验证
curl -s http://127.0.0.1:19223/json | python3 -c "import json,sys; pages=json.load(sys.stdin); [print(f\"{p['title'][:40]:40s} | {p['url'][:60]}\") for p in pages]"
```

## 3. 登录恢复

CDP 恢复后如果店小秘 session 过期：

### 优先：问用户扫码（最快）

```python
# 在 debug Chrome 中导航到店小秘
page = ctx.pages[0]
page.goto('https://www.dianxiaomi.com/index.htm')

# 找到扫码登录入口
page.evaluate("""() => {
    const el = document.querySelector('.toggle-way.way-scan, [class*=way]');
    if (el) el.click();
}""")
page.screenshot(path='/tmp/dxm_qr.png')
# → 发送 MEDIA:/tmp/dxm_qr.png 给用户扫码
```

### 备选：账号密码（需用户提供验证码）

```python
page.locator('#userName').fill('username')
page.locator('#exampleInputPassword').fill('password')
# → 截图验证码 → 发 MEDIA 给用户看
page.screenshot(path='/tmp/dxm_captcha.png')
# 用户回复验证码后填入：
page.locator('#verifyCode').fill('ABCD')
page.locator('button').filter(has_text='登录').click()
```

### ❌ 绝不用：OCR 自动破解（已证实 20+ 次全部失败）

- tesseract: 每次识别结果不同，服务端校验全部失败
- ddddocr: 同样全部失败
- 尝试：「验证码填写错误」

## 4. 恢复后验证

CDP + 登录都恢复后：

```python
# 确认可操控页面
page.evaluate("document.title")
# 导航到采集箱
page.goto('https://www.dianxiaomi.com/web/smt/smtProductList/draft')
# 确认产品列表加载
page.evaluate("document.body.innerText.substring(0, 500)")
```

## 5. 时间盒

- 诊断阶段：≤ 30秒
- 恢复阶段：≤ 3分钟
- 超过 3 分钟 → 切换降级方案（书签采集/用户手动操作）

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*