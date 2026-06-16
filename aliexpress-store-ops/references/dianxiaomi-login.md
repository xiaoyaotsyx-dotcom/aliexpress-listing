# 店小秘登录 — 浏览器自动化的关键模式与陷阱

> 记录 Hermes Agent 通过 Playwright/CDP 自动登录店小秘的工作流、坑点和已验证的解决方案。

## 📌 核心策略：优先走 CDP 直连用户 Chrome（2026-06-11 确认）

**最佳方案：** 如果用户的 Windows Chrome 已登录店小秘（`relay2.py` 在运行），直接通过 CDP 连接即可，**完全不需要验证码**。

```python
# WSL 端检测 CDP 是否在线
import urllib.request, json
GW = "172.24.48.1"  # WSL 网关 IP: $(ip route show default | awk '{print $3}')
try:
    req = urllib.request.urlopen(f"http://{GW}:19223/json/version", timeout=5)
    info = json.loads(req.read())
    print(f"CDP 在线！Browser: {info['Browser']}")
    # 然后通过 playwright.connect_over_cdp(info['webSocketDebuggerUrl']) 连接
except:
    print("CDP 不可用，走 Hermes browser tool 登录")
```

**无需走 Hermes browser tool 的 captcha 流程** — 用户 Chrome 中店小秘的登录态被 CDP 中继复用。（已验证：用户的 Chrome 会保持 `https://www.dianxiaomi.com/web/home` 登录态，cookie 长度 > 800 字符。）

> ⚠️ CDP 原始 websocket 连接（`websocket-client` Python 库）约 10-15 秒后断开。**始终用 Playwright 的 `connect_over_cdp()`** 来保证连接稳定。

## 登录页结构

| 元素 | 可用的选择方式 |
|:--|:--|
| 用户名输入 | Snapshot ref `@e68` / 或 `#exampleInputName` (Playwright) |
| 密码输入 | Snapshot ref `@e69` / 或 `#exampleInputPassword` (Playwright) |
| 验证码输入 | Snapshot ref `@e70` / 或 `input[name="verifyCode"]` (不稳定) |
| 验证码图片 | `#verifyImgCode` (JS 可用) 或 `img[src*="verify/code"]` |
| 登录按钮 | Snapshot ref `@e66` / 或 `#loginBtn` |
| "记住密码"勾选框 | Snapshot ref `@e83` (默认已勾选) |

## ⚠️ 关键坑点：店小秘不支持邮箱登录！

**这是今天（2026-06-08）反复登录失败的根本原因。**

店小秘登录页面**明确禁止邮箱登录**，只接受用户名：

```javascript
// 登录函数 login() 源码片段
if (exampleInputName.indexOf('@') !== -1) {
    $userVerify.html('暂不支持邮箱登录，请使用用户名登录！');
    return false;  // 登录在这里被拦下，根本不会提交
}
```

| 做法 | 结果 |
|:--|:--|
| `page.fill('#exampleInputName', '[你的店小秘邮箱]')` | ❌ 被拦截，显示「暂不支持邮箱登录」 |
| `page.fill('#exampleInputName', '[你的店小秘用户名]')` | ✅ 正常提交 |

### 用户名来源

用户信息（记忆）：[你的店铺名称]店主（店小秘账号：[你的店小秘用户名]）

| 字段 | 值 |
|:--|:--|
| 店小秘用户名 | `[你的店小秘用户名]` |
| 关联邮箱 | `[你的店小秘邮箱]`（仅用于找回密码，不可用于登录） |
| 登录密码：[你的店小秘密码] |

### 登录失败的迹象

- Playwright 点了登录按钮后页面**没有跳转**，仍停留在 `index.htm`
- `#exampleInputName` 输入框**边框变红**（`border-color: #ec4339`）
- `.userVerify` 元素包含文本 `暂不支持邮箱登录，请使用用户名登录！`（但该元素可能隐藏较深，不容易被 `text_content()` 发现）
- 没有任何 alert/error banner 弹出来（因为错误只显示在 `.landing` 区域）
- 相比之下的正确错误提示：验证码错误时会出现明显的「验证码错误」提示文本

### 为什么这个问题容易错过

1. 页面 URL 没变（仍是 `index.htm`），看起来像验证码错误
2. 没有弹窗或 alert，页面静默失败
3. `.userVerify` 的错误文本在 DOM 深处，Playwright 的 `page.text_content()` 不一定能抓到
4. 输入框边框变红需要截图才能看到
5. 连续多次登录失败会让人以为是验证码 OCR 问题或反爬机制，实际上原因是完全不同的

Hermes 的 `browser_navigate` / `browser_snapshot` 返回的 DOM ref IDs **有时效性**：

- Ref 只在**紧跟着 navigation/snapshot 的同一轮 tool call 之后**有效
- 一旦页面闲置数秒，`browser_snapshot` 返回 `(empty page)`，所有 ref 失效
- 失效后 `browser_type(ref)` 报 `"Unknown ref: eXX"`
- 浏览器内部可能通过 `about:blank` 重置了页面

**关键现象：** 经过多轮尝试，ref 在用户回复消息期间几乎必然过期。这是 Hermes browser tool 的已知行为，不是操作失误。

## ✅ 已验证的最佳登录流程（2026-06-08 验证）

### ⚠️ `login.htm` 已失效（2026-06-11 确认）

**旧 URL `https://www.dianxiaomi.com/login.htm` 现在返回 404「页面地址有误或者不存在」！** 登录表单已整合到首页，入口为：

```
https://www.dianxiaomi.com/index.htm
```

以下所有流程均已使用 `index.htm`。如果看到 404 错误，确认 URL 是否正确。

### 步骤 A：导航 + 立即填账号密码（同一轮）

```tool-call-flow
1. browser_navigate(url="https://www.dianxiaomi.com/index.htm")
   ← 返回 snapshot，refs @e68 @e69 @e70 @e66 均有效

2. browser_type(ref="@e68", text="[你的店小秘邮箱]")
3. browser_type(ref="@e69", text="[你的店小秘密码]")
   ← refs 此刻还新鲜，填写成功
```

### 步骤 B：获取当前验证码（不导航、不刷新）

```tool-call-flow
4. browser_console(expression="document.querySelector('img[src*=\\\"verify/code\\\"]')?.src")
   ← 返回 captcha URL，如 "https://www.dianxiaomi.com/verify/code.htm?t=[PHONE_REDACTED]88"

5. terminal(command="curl -s -o /tmp/captcha_go.jpg '<captcha_url>' && cp /tmp/captcha_go.jpg 'C:/Users/[你的用户名]/Desktop/captcha_go.jpg'")
```

### 可选技巧：验证码 JS 刷新（保持页面存活）

如果 refs 还有效但验证码已过期，可以用 JS 原地刷新验证码**不触发页面导航**，这样 refs 继续保持有效：

```javascript
// 在 browser_console 中执行
document.querySelector('img[src*="verify/code"]').src =
    'https://www.dianxiaomi.com/verify/code.htm?t=' + Date.now();
```

这比 `browser_navigate` 好在哪里：
- 不触发页面全量加载 → refs @e68 @e69 @e70 @e66 保持有效
- 用户名密码已填入的不丢失
- 新 captcha URL 可以通过 `browser_console` 立即获取

**适用场景：** refs 刚获取但 captcha 图片已超时（例如页面加载后等了几秒才访问）。

### 步骤 C：告知用户

```markdown
![验证码](MEDIA:/tmp/captcha_go.jpg)
桌面也有 → `C:\Users\[你的Windows用户名]\Desktop\captcha_go.jpg`
老板看一眼告诉我！
```

### 步骤 D：用户回复验证码后 → 填入 + 登录

**⚠️ 问题：** 此时 refs 几乎肯定已过期（浏览器闲置数秒），`browser_type(@e70)` 会失败。

**尝试过的方案及结果：**

| 方案 | 结果 |
|:--|:--|
| `browser_type(ref)` 直接填验证码 | ❌ ref 过期，报 `Unknown ref` |
| 用 JS 通过 ID 设置值 | ❌ `document.querySelector('input[placeholder*="验证码"]')` 返回 null（登录表单可能不在常规 DOM 树） |
| `browser_navigate` 重进页面 → 用新 ref | ❌ 新导航生成新验证码，旧码作废，无限循环 |
| 连续 `browser_navigate` + 立即填所有字段 | ✅ 最可靠，但需要用户**在同一轮**提供验证码 |

**当前最优方案：** 要求用户在验证码图片这条消息上直接回复 code，Agent 在下一轮：
1. 立即 `browser_navigate`（生成新验证码）
2. 用返回的 snapshot ref 立即填 username + password + captcha + click login
3. **全部在一个 response 里完成**

此方案假设用户给的新 code 对新验证码也适用（风险：如果两个验证码不同则登录失败）。失败时用户可再次提供。

## ⚠️ OCR 不可行

Tesseract 5 + PIL 预处理（对比度增强、阈值二值化、4x放大）对店小秘 104×32 扭曲验证码的识别率**接近 0%**，不要依赖。

### 尝试过的 OCR 方法（全部失败）

- 灰度 + 对比度增强 + 阈值 → 输出空
- 各种 psm 模式（7/8/13）→ 乱码
- 分离 RGB 通道分别 OCR → 不一致
- 5次取不同的 captcha → 均无法可靠识别

**结论：** 店小秘验证码专门设计为抗 OCR，必须走人眼识别路径。

## ⚠️ 验证码图片保存路径 — 桌面卫生（重要！）

**用户已明确抗议：不要在桌面上扔一堆验证码临时文件！**

✅ 正确做法：
- 验证码保存到 `/tmp/dxm_captcha.png`（仅1份）
- 在聊天中用 `MEDIA:/tmp/dxm_captcha.png` 内联显示
- 如果必须放桌面，用**固定文件名**（如 `C:\Users\[你的Windows用户名]\Desktop\dxm_captcha.png`），每次覆盖，不产生新文件

❌ 错误做法：
- 每次用不同文件名 → 桌面垃圾堆
- 同时多种格式保存 → 用户分不清哪张有效

## 验证码图片保存路径

Windows 桌面路径（仅限紧急备用）：
```
C:/Users/[你的用户名]/Desktop/dxm_captcha.png 
```
对应的 Windows 路径（给用户看）：
```
C:\Users\[你的Windows用户名]\Desktop\dxm_captcha.png
```

**桌面文件存储规则（2026-06-08 用户明确）：**
- 最多在桌面留 **1 张** captcha 图片
- 用 **固定文件名** `dxm_captcha.png`，每次覆盖
- 绝不用不同文件名（captcha_go.jpg, captcha_live.jpg, captcha_now.jpg 等）—— 用户抗议过
- **优先方案：** 保存到 `/tmp/` 并通过 `MEDIA:/tmp/dxm_captcha.png` 在聊天内联显示，不碰桌面
- 用户回复 code 后立即清理桌面临时文件

### 获取清晰 captcha 的方法（优先顺序）

| 方法 | 效果 | 说明 |
|:--|:--|:--|
| ① `browser_vision` → 取 screenshot_path | ⭐ 全页截图，需裁剪 | vision 可能 401 失败，但 **screenshot_path 始终可用**，裁剪后 MEDIA 发送 |
| ② Playwright 元素截图 | ⭐ 仅 captcha 元素，清晰 | `captcha_img.screenshot(path="/tmp/dxm_captcha.png")` - 最清晰 |
| ③ 下载 captcha URL（curl） | ✅ 与原图相同 | `curl -s -o /tmp/dxm_captcha.png <captcha_url>` |

**MEDIA 裁剪技巧：** 全页截图太大 → 用 PIL 裁剪到登录区域（右 420×250px），再发送。如果用户看不清（说"验证码是什么"），尝试：
- 裁剪得更小（仅 captcha 元素区域 ~120×40px）
- 放大 3x 再用 `Image.LANCZOS`
- 或者刷新验证码重新截图（验证码可能本身模糊）

## ⚠️ JS querySelector 在 Hermes browser tool 中不可用

经过多轮测试，店小秘登录表单元素**无法通过 Hermes browser_console 的 JS querySelector 访问**：

```javascript
// ❌ 全部返回 null
document.querySelector('input[placeholder*="用户名"]')
document.querySelector('#exampleInputName')
document.querySelector('input[name="account"]')
document.querySelector('input[placeholder*="验证码"]')
document.querySelector('#verifyCode')
```

即使 `browser_snapshot` 明确显示这些元素（`textbox "请输入用户名" [ref=e68]`），它们**不在常规的 JS DOM 查询路径中**。可能的原因：
- 登录表单在 shadow DOM 或 iframe 中
- snapshot 的 accessibility tree 解析与真实 DOM 不同
- 某些前端框架的动态渲染导致 DOM 在 JavaScript 层面不可达

**已验证的有效方法：**
- ✅ `browser_type(ref)`（snapshot refs）— 导航后立即使用
- ✅ Playwright `page.fill('#exampleInputName', ...)` — 独立进程中正常运行
- ❌ `browser_console` 中任何 `document.querySelector` — 全部失败

这个限制解释了为什么 `browser_type` 的 refs 是唯一可靠的 Hermes 原生登录方式，也解释了为什么 refs 一过期就陷入死循环。

## 🚀 Playwright 脚本方案（推荐，2026-06-08 验证）

**解决了 Hermes browser tool ref 过期的核心问题。** 用独立的 Playwright headless 浏览器进程，通过文件 IPC 实现跨轮交互。

### 工作流

```
Agent: 启动 scripts/dianxiaomi-login.py（background）
  → 打开 headless Chromium
  → 填账号密码
  → 下载当前验证码到桌面
  → 等待 /tmp/dxm_code.txt 出现

Agent: 通知用户看验证码（MEDIA + 桌面路径）

用户: 回复验证码 "ABC123"

Agent: echo "ABC123" > /tmp/dxm_code.txt
  → 后台脚本读取 code
  → 填验证码 → 点登录
  → 验证成功 → 保持浏览器存活
  → 写 /tmp/dxm_state.json {"status": "logged_in"}
```

### 也支持 stdin 交互（pty 模式）

Playwright 脚本也可以通过 `pty=True` 运行并直接从 stdin 读取验证码，不需要文件 IPC：

```python
# 启动（background, pty=True）
terminal(
    command="python3 /tmp/login_stdin.py",
    background=True,
    pty=True,     # 启用交互模式
    timeout=300
)

# 脚本输出 "ENTER_CODE:" 后，用 submit 发验证码
process(action="submit", session_id="...", data="ABC123")
```

这种模式更适合一次性登录+直接跳转到编辑页的场景。缺点是 pty 模式下输出读取可能有延迟。

### 登录成功检测（重要改进）

⚠️ **店小秘登录页和登录后首页都是同一个 URL：**`https://www.dianxiaomi.com/index.htm`

```python
# ❌ 错误示范：靠 URL 判断登录状态
if "/index.htm" not in page.url:  # 永远为 False，index.htm 就是登录页
```

```python
# ✅ 正确做法 1：检测 login form 是否消失
is_logged_in = page.query_selector('#exampleInputName') is None

# ✅ 正确做法 2：检测页面内容中的错误提示
error_text = page.evaluate("""() => {
    const els = document.querySelectorAll('*');
    for (const el of els) {
        const t = el.textContent?.trim() || '';
        if (t.includes('验证码错误') || t.includes('密码错误') || ...) {
            return t.slice(0, 100);
        }
    }
    return '';
}""")
```

支持的错误关键词：`验证码错误`、`密码错误`、`用户名不存在`、`账号不存在`、`暂不支持邮箱登录`。空字符串 = 登录成功。

### 常见登录失败原因速查表

| 现象 | 可能原因 | 验证方法 |
|:--|:--|:--|
| 点登录后页面没动，无错误提示 | 使用了邮箱登录 | 检查 `#exampleInputName` 边框是否变红，`.userVerify` 内容 |
| 页面显示 `验证码错误` 提示 | 验证码输错了 | 刷新验证码重试 |
| 按钮灰色不可点击 | 表单验证未通过 | 检查各字段是否已填 |
| 连错多次后验证码不刷新 | 服务器端 ratelimit | 等 30 秒重试 |

### 优势

| 方面 | Hermes browser tool | Playwright 脚本 |
|:--|:--|:--|
| 页面存活 | 数秒内变 `(empty page)` | 进程存活期间一直有效 |
| Captcha 一致性 | 每次 navigate 刷新 | 同一页面不刷新，验证码匹配 |
| 跨轮交互 | ref 过期无法填 | 文件 IPC 无延迟 |
| 登录后 | 丢失控制 | 保持浏览器，可继续导航到编辑页 |

### 使用方法

```python
# 1. 启动（background, notify_on_complete=True）
terminal(
    command="python3 /tmp/dxm_login.py",
    background=True,
    notify_on_complete=True,
    timeout=600
)

# 2. 等待输出 CREDENTIALS_OK + CAPTCHA_SAVED
# 确认 /tmp/dxm_state.json 为 waiting_for_code

# 3. 通知用户看验证码（MEDIA + 桌面路径）

# 4. 用户回复后，写 code 到 IPC 文件
terminal('echo "ABC123" > /tmp/dxm_code.txt')

# 5. 等待脚本完成（notify 或 process wait）
# 检查 /tmp/dxm_state.json → logged_in

# 6. 后续导航到编辑页
terminal('echo "NAV:https://www.dianxiaomi.com/web/smt/edit?id=xxx" > /tmp/dxm_code.txt')
```

### 元素选择器（已验证）

| 字段 | CSS Selector |
|:--|:--|
| 用户名 | `#exampleInputName` |
| 密码 | `#exampleInputPassword` |
| 验证码 | `#verifyCode` |
| 登录按钮 | `#loginBtn` |
| 验证码图片 | `img[src*="verify/code"]` |

### 已知问题

- Playwright headless 启动需 2-3 秒初始化
- 首次运行需有 craplet 缓存（`python3 -m playwright install chromium` 已完成）
- 脚本用 `--no-sandbox` 参数（WSL 环境必需）
- Captcha 图片会保存到桌面和 `/tmp/captcha_login.jpg`
- **文件 IPC 细节：** `STATE_FILE` 的状态变化可能延迟 1-2 秒（脚本每秒检查一次），提交 code 后需等 3-4 秒才能看到状态更新

### Captcha 元素截图 vs URL 下载（2026-06-08 验证）

两种方式获取的验证码图片**完全相同**（已验证：`captcha_element.screenshot()` 和 `urllib.request.urlretrieve(url)` 返回同一张图），但元素截图更可靠，因为直接截取渲染后的 DOM 元素，不受服务端二次生成影响。

```python
# ✅ 推荐：直接截取页面上的 captcha 元素
captcha_img = page.query_selector('img[src*="verify/code"]')
captcha_img.screenshot(path="/tmp/captcha.png")

# 备选：通过 URL 下载（效果相同，但多一次 HTTP 请求）
src = captcha_img.get_attribute('src')
urllib.request.urlretrieve(f"https:{src}", "/tmp/captcha.jpg")
```

**即使使用元素截图，Tesseract OCR 仍然不可靠。** 店小秘验证码（104×33 含扭曲字符）专门设计为抗 OCR，不要依赖任何自动识别方案。

### Storage State 持久化（不工作）

Playwright 的 `context.storage_state()` 能保存 cookies + localStorage，理论上可以跨运行复用登录态：

```python
# 登录成功后保存
context.storage_state(path="/tmp/dxm_storage.json")

# 下次启动时加载
context = browser.new_context(
    storage_state="/tmp/dxm_storage.json",
    ...
)
```

**⚠️ 2026-06-08 测试结果：** 店小秘的 cookies 似乎无法跨浏览器进程复用。尝试过 `add_cookies()` + `storage_state()` 两种方式，加载后访问编辑页仍然被重定向到登录页。可能原因：
- 服务端 IP 绑定检查（headless 每次 IP 不同？）
- session 复用了 localStorage 中不在 storage_state 范围的 key
- 登录成功后服务端下发短时效 token（< 1 min）

**当前结论：** 不依赖持久化，每次重启 Playwright 脚本时预期需要重新登录。

### 编辑页 URL（重要！）

登录成功后导航到编辑页的**两个 URL 行为不同**：

| URL 格式 | 结果（2026-06-08 验证） |
|:--|:--|
| `/product/edit.htm?id={id}` | ❌ **始终重定向到 `index.htm`**（`wait_until="domcontentloaded"` 也会重定向） |
| `/web/smt/edit?id={id}` | ✅ 应正常显示编辑页（SKILL.md 中已记录） |

原因：店小秘可能在 2025-2026 年迁移了路由，旧 URL 不再支持直接访问。**ALWAYS 用 `/web/smt/edit` 路径。**

### 登录函数细节

登录按钮触发的是异步 JS 函数 `async function login(type)`，点击按钮后：
1. 校验表单字段（用户名不能含 `@`、密码非空、验证码非空）
2. 通过 jQuery AJAX 提交到后端
3. 后端验证通过后重定向到首页

表单 `#loginForm` 的 `method="get"` 和 `action="https://www.dianxiaomi.com/index.htm"` — 这是**模拟的**，实际提交由 JS 控制。

### 完整脚本

见 `scripts/dianxiaomi-login.py` — 可直接调用，含文件 IPC、超时处理、登录后浏览器保持。

## MEDIA 嵌入的注意点

Feishu `MEDIA:/absolute/path` 引用的是 tool 执行时的文件内容。如果同一轮 response 中先 terminal 下载了新的验证码，再用 `MEDIA:/tmp/same_file.jpg`，MEDIA 会上传终端命令**之后**的最新文件。但如果之前已经上传过同名文件，Feishu 可能缓存旧版本。

**最佳做法：** 每次用不同文件名 + 先 terminal 下载再在 response 中 MEDIA 引用。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*