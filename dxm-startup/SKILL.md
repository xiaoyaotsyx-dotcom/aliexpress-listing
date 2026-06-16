---
name: dxm-startup
description: 速卖通上架——启动模块：Chrome CDP调试模式启动 + Relay中继链 + Playwright连接 + 登录检查
domain: ecommerce
triggers:
  - 用户说"开始上架"、"连接浏览器"、"启动Chrome"、"relay断了"
  - CDP连不上时
---

# 启动模块：Chrome + Relay + Playwright

## 架构

```
Windows Chrome (--remote-debugging-port=9222)
  ↕ Relay2.exe (0.0.0.0:9255 → 127.0.0.1:9222)
Windows IP (172.24.48.1:9255)
  ↕ WSL chrome_relay.py (127.0.0.1:19223 → 172.24.48.1:9255)
  ↕ Playwright connect_over_cdp('http://127.0.0.1:19223')
```

## Step A：启动Chrome（Windows）

```bash
# 先杀掉旧Chrome进程
taskkill /F /IM chrome.exe

# 启动Chrome带调试端口
cmd.exe /c start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\Users\[你的Windows用户名]\Desktop\chrome-debug"
```

⚠️ 必须用独立 `--user-data-dir`（如 `chrome-debug`），默认profile绑不了9222。

## Step B：启动Relay2（Windows）

Relay2.exe应在 Windows 启动项自动运行：
`C:\Users\[你的Windows用户名]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\hermes-gateway.vbs`

手动启动：双击运行 Relay2.exe。

## Step C：启动WSL Relay

```bash
cd ~/.hermes/scripts && python3 chrome_relay.py &
```

## Step D：验证链路

```bash
# 检查WSL relay
curl -s http://127.0.0.1:19223/json | head -5

# 应返回Chrome标签页列表的JSON
```

## Step E：Playwright连接

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp('http://127.0.0.1:19223')
    pages = browser.contexts[0].pages
    # 检查已打开的标签页
```

## 登录检查

### 店小秘登录

导航到店小秘 → 检查是否已登录（看页面是否有 `[你的店小秘用户名]` 用户名）：
```javascript
document.body.innerText.includes('[你的店小秘用户名]')
```

未登录时用二维码登录：店小秘右上角 → 扫码登录。

### 1688登录

检查1688登录状态：打开1688任意产品页 → 看是否有"登录"按钮。
```javascript
document.body.innerText.includes('登录')
```

未登录时手动登录（1688验证码无法自动化）。

## 故障恢复

### Gateway断连后重连铁律

**致命错误：** 直接调用 `browser_navigate` 会创建新标签页，丢失已填数据。

**正确步骤：**
```
1. browser_cdp → Target.getTargets     # 列出所有标签页
2. 找到店小秘编辑页（title="店小秘--编辑速卖通产品"）
3. Runtime.evaluate 读取页面状态（标题/hash/bodyText）
4. 确认哪个标签页有已填数据
5. Target.closeTarget 关闭空白/重复标签页
6. Target.activateTarget 激活正确标签页
7. 此时 browser_snapshot 应显示已填数据
```

### 全链挂了

```bash
# WSL端
pkill -f chrome_relay.py
cd ~/.hermes/scripts && python3 chrome_relay.py &

# Windows端（需手动或从WSL触发）
taskkill /F /IM chrome.exe
# 重新启动Chrome（Step A）
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*