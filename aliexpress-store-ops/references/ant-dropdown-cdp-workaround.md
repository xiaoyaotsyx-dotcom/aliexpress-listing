# Ant Design Dropdown 菜单项操作技巧

## 核心发现（2026-06-10）

**Ant Design 的 Dropdown 组件（非 Select）在 CDP 模式下，下拉菜单的 DOM 始终存在于页面中，但 `display` 属性被设为 `none`（父容器隐藏）。**

这意味着：
1. 鼠标点击触发按钮（如「上传文件」）→ 视觉上下拉菜单应该弹出
2. **但在 CDP (`connect_over_cdp`) 模式下，Ant Design 的 overlay 渲染机制有时不会正确地将 dropdown 设为可见**
3. 然而，**菜单项的 `.ant-dropdown-menu-item` DOM 元素始终在页面中**，只是它的父级 `.ant-dropdown` 被隐藏
4. 可以直接通过 JS 点击菜单项，事件仍然会正常触发

## ✅ 已验证的解决方案：Playwright file_chooser 拦截（2026-06-09 唯一成功方案）

见下方「商品说明书上传：Playwright 文件选择器拦截」章节。

## ⚠️ 历史方案（仅作参考）

以下方案仅对**非 Vue 3 组件**有效。对店小秘的 Vue 3 + Ant Design 组件无效。

```python
# 1. 先用鼠标坐标点击触发按钮（保持用户可见的体验）
btn_coord = page.evaluate("""() => {
    var btns = document.querySelectorAll('button');
    for (var i = 0; i < btns.length; i++) {
        if (btns[i].textContent && btns[i].textContent.indexOf('上传文件') != -1 && btns[i].offsetParent !== null) {
            var r = btns[i].getBoundingClientRect();
            return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
        }
    }
}""")
page.mouse.click(btn_coord['x'], btn_coord['y'])
time.sleep(2)

# 2. 直接找到菜单项，强制触发点击（无视父容器是否可见）
page.evaluate("""() => {
    var items = document.querySelectorAll('.ant-dropdown-menu-item');
    for (var i = 0; i < items.length; i++) {
        if (items[i].textContent.indexOf('图片空间(PDF)') != -1) {
            items[i].click();
            items[i].dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
            items[i].dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
            items[i].dispatchEvent(new MouseEvent('click', {bubbles: true}));
            return;
        }
    }
}""")
# 菜单项点击后，关联的弹窗/操作会正常触发
```

## 适用场景

这个方法适用于 **所有 Ant Design Dropdown 组件**（即 `<a class="ant-dropdown-trigger">` 或带 `ant-dropdown-trigger` 的元素触发的菜单），包括但不限于：

| 场景 | 菜单项 | 效果 |
|:--|:--|:--|
| 商品说明书上传 | 本地上传 / 上传URL链接 / 图片空间(PDF) | ✅ 弹窗打开 |
| 产品图片选择 | 本地图片 / 空间图片 / 网络图片 | ✅ 弹窗打开 |
| 产品视频上传 | 本地上传 / 网络上传 / 从速卖通视频库选择 | ✅ 弹窗打开 |
| 营销水印 | 普通水印 / 营销水印 | ✅ 弹窗打开 |

## ⚠️ CDP 文件上传 — 根本性限制（2026-06-15 更新）

### 核心结论：Vue 3 响应式系统清除了 CDP 注入的文件

经过深入测试（2026-06-15），`DOM.setFileInputFiles` 对店小秘的 `<input type="file">` 返回成功但文件不持久。**根本原因不是 Shadow DOM，而是 Vue 3 的响应式重渲染：**

1. **DOM.setFileInputFiles 确实写入了文件** — `DOM.describeNode({backendNodeId})` 确认元素是 file input 且无 user-agent shadow root 阻挡
2. **但 Vue 3 组件在 `dispatchEvent(change)` 后重渲染**，重建了整个 `<input>` 元素，丢失了 CDP 注入的文件引用
3. **Ant Design Vue 表单校验绑定在内部 `reactive` 状态上**，不读取 DOM 的 `files` 属性，因此校验永远显示「请上传文件！」

### 验证数据

```javascript
// CDP 返回成功
DOM.setFileInputFiles({backendNodeId: 15402, files: ["C:\\Users\\[你的Windows用户名]\\Desktop\\风扇说明书.pdf"]})
// → {"result": {}}  ✅

// 立即检查 — 文件存在！
Runtime.evaluate({expression: "document.querySelector('#localFileUploadInp').files.length"})
// → {"value": 0}  ❌ 文件已被清理
```

**关键：** `DOM.describeNode` 返回中 `shadowRoots` 是 Chrome 原生的 user-agent shadow root，这是标准行为。**它不阻止文件写入。** 真正阻止文件保留的是 Vue 的 re-render 生命周期。

### 已验证的文件注入方法（能写入但被 Vue 清除）

#### 方法 A：CDP WebSocket + base64 + File 构造函数（2026-06-15 发现）

通过 Python WebSocket 直接连接 CDP，将 PDF 文件 base64 编码后注入：

```bash
# WSL 端
python3 -c "
import base64
with open('/mnt/c/Users/用户名/Desktop/风扇说明书.pdf', 'rb') as f:
    data = f.read()
b64 = base64.b64encode(data).decode()
with open('/tmp/pdf_b64.txt', 'w') as f:
    f.write(b64)
"

# CDP WebSocket 注入脚本 (Python + websockets 库)
cat > /tmp/inject_pdf.py << 'PYEOF'
import json, asyncio
import websockets
CDP_WS = 'ws://127.0.0.1:19223/devtools/browser/浏览器ID'
TARGET_ID = '页面TargetID'
with open('/tmp/pdf_b64.txt') as f:
    b64 = f.read()
async def main():
    async with websockets.connect(CDP_WS, max_size=10*1024*1024) as ws:
        # 1. Attach to target
        await ws.send(json.dumps({"id":1,"method":"Target.attachToTarget",
            "params":{"targetId":TARGET_ID,"flatten":True}}))
        resp = json.loads(await ws.recv())  # attachedToTarget event
        resp2 = json.loads(await ws.recv()) # response
        session_id = resp2['result']['sessionId']
        # 2. Evaluate JS to inject file
        js = f'''
(async function() {{
    var b64 = "{b64}";
    var binaryStr = atob(b64);
    var bytes = new Uint8Array(binaryStr.length);
    for (var i = 0; i < binaryStr.length; i++)
        bytes[i] = binaryStr.charCodeAt(i);
    var file = new File([bytes], '风扇说明书.pdf', {{type:'application/pdf'}});
    var input = document.querySelector('#localFileUploadInp');
    var dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    ['change','input','blur'].forEach(function(n) {{
        input.dispatchEvent(new Event(n, {{bubbles:true}}));
    }});
    return JSON.stringify({{files:input.files.length,size:file.size}});
}})()
'''
        await ws.send(json.dumps({"id":2,"sessionId":session_id,
            "method":"Runtime.evaluate","params":{"expression":js,
            "returnByValue":true,"awaitPromise":true,"timeout":120000}}))
        print(json.loads(await ws.recv()))
asyncio.run(main())
PYEOF
python3 /tmp/inject_pdf.py
```

**结果：** `{"ok":true,"size":132691,"files":1}` — 文件成功写入。但 Vue 重渲染后 `files` 归零。

#### 方法 B：DataTransfer 注入（同方法 A 的 JS 逻辑，用 Hermes browser_cdp 工具）

```javascript
Runtime.evaluate({
  expression: `
    var b64 = "base64data...";
    var binaryStr = atob(b64);
    var bytes = new Uint8Array(binaryStr.length);
    for(var i=0;i<binaryStr.length;i++) bytes[i]=binaryStr.charCodeAt(i);
    var file = new File([bytes], '风扇说明书.pdf', {type:'application/pdf'});
    var input = document.querySelector('#localFileUploadInp');
    var dt = new DataTransfer();
    dt.items.add(file);
    input.files = dt.files;
    input.dispatchEvent(new Event('change', {bubbles:true}));
  `,
  returnByValue: true
})
```

**局限：** base64 数据很大时（132KB PDF → 177KB base64），Hermes browser_cdp 的表达式长度有限。需要用 WebSocket 方式绕过。

### ✅ 唯一可自动化的方案：Playwright `expect_file_chooser()` + file picker 拦截（2026-06-09 发现）

**核心思路：** 不用 CDP 直接写 input，而是用 Playwright 拦截 Chrome 的原生文件选择对话框，让操作系统来"选择"文件。

#### 前置条件

```bash
pip3 install playwright
```

#### 完整上传代码

```python
import time
from playwright.sync_api import sync_playwright

CDP = 'http://127.0.0.1:19223'  # WSL CDP relay port
PDF = '/mnt/c/Users/用户名/Desktop/风扇说明书.pdf'  # WSL 路径

with sync_playwright() as pw:
    browser = pw.chromium.connect_over_cdp(CDP)
    
    # 1. 找到编辑页标签
    page = None
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if 'edit?id=产品ID' in pg.url and 'devtools' not in pg.url:
                page = pg; break
        if page: break
    
    page.bring_to_front()
    
    # 2. 滚动到上传按钮
    page.evaluate("""() => {
        var mu = document.querySelector('.manual-upload');
        if (mu) mu.scrollIntoView({block: 'center'});
    }""")
    time.sleep(1)
    
    # 3. 注册文件选择器拦截 → 打开上传菜单
    with page.expect_file_chooser() as fc_info:
        # 3a. 点击「上传文件」按钮
        coord = page.evaluate("""() => {
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent && btns[i].textContent.includes('上传文件')
                    && btns[i].offsetParent) {
                    var r = btns[i].getBoundingClientRect();
                    return {x: r.x + r.width/2, y: r.y + r.height/2};
                }
            }
        }""")
        if coord:
            page.mouse.click(coord['x'], coord['y'])
            time.sleep(1.5)
        
        # 3b. JS 点击「本地上传」菜单项（dropdown 可能隐藏，但 Ant Design 事件仍触发）
        page.evaluate("""() => {
            var items = document.querySelectorAll('.ant-dropdown-menu-item');
            for (var i = 0; i < items.length; i++) {
                if (items[i].textContent && items[i].textContent.includes('本地上传')
                    && !items[i].textContent.includes('网络') && !items[i].textContent.includes('空间')) {
                    items[i].click();
                    items[i].dispatchEvent(new MouseEvent('click', {bubbles: true}));
                    return;
                }
            }
        }""")
        time.sleep(2)
        
        # 3c. 直接点击隐藏的 file input（触发原生文件选择器）
        page.evaluate("() => document.querySelector('#localFileUploadInp')?.click()")
        time.sleep(1)
        
        # 4. 文件选择器被拦截 → 设置文件
        fc = fc_info.value
        fc.set_files(PDF)
        time.sleep(2)
    
    # 5. 验证
    upload_text = page.evaluate("""() => {
        var mu = document.querySelector('.manual-upload');
        return mu ? mu.textContent.trim() : 'not found';
    }""")
    print(f"Upload result: {upload_text}")
    if '.pdf' in upload_text:
        print("✅ 上传成功！")
```

#### 为什么这种方法有效

| 方法 | 是否成功 | 原因 |
|:--|:--:|:--|
| CDP `DOM.setFileInputFiles` | ❌ | Vue 3 重渲染清除文件 |
| Base64 → DataTransfer 注入 | ❌ | 同上 |
| Hermes browser_cdp mouse.click | ❌ | Ant Design 不响应程序化事件 |
| **Playwright file_chooser 拦截** | ✅ | 触发真实系统文件对话框 → Ant Design 正确处理 |

Playwright 的 `expect_file_chooser()` + `set_files()` 方法绕过了所有上述问题，因为它：
1. 先通过 `page.mouse.click()` 和 JS `.click()` 触发 Ant Design 的事件链
2. 用 `set_files()` 通过 CDP 协议设置文件（Playwright 内部处理了事件分发）
3. Ant Design 组件收到系统级文件选择完成信号，正确上传到服务器

#### 注意事项

- **路径必须用 WSL 格式**：`/mnt/c/Users/用户名/Desktop/file.pdf`（不能用 `C:\...`）
- **Playwright `connect_over_cdp` 接收 HTTP 地址**：`http://127.0.0.1:19223`（不是 WebSocket URL）
- **文件选择器可能不会立即触发**：需要依次点击「上传文件」→「本地上传」→ 再点隐藏 input
- **时间等待：** 各步骤间需要 1-2 秒等待 Ant Design 处理事件链
- **多个编辑页标签**：如果打开多个编辑页，用 URL 过滤找到正确的那个

### DOM 操作通用技巧：用 backendNodeId 替代 nodeId（2026-06-15 发现）

虽然 `DOM.setFileInputFiles` 不适用于 user-agent shadow DOM input，但 `backendNodeId` 的引用方式对其他 DOM 操作仍然有效：

```javascript
// DOM.querySelector() 在 CDP 下常常失败
DOM.querySelector({nodeId: 5, selector: "#localFileUploadInp"})
// → "Could not find node with given id"

// 改用 backendNodeId（从 DOM.getDocument({depth: -1}) 搜索获取）
DOM.describeNode({backendNodeId: 15402})
// → 成功返回节点信息

// 适用于：
// - DOM.setAttributes
// - DOM.getOuterHTML
// - DOM.removeNode
// - DOM.setNodeValue
// - ❌ DOM.setFileInputFiles（对 user-agent shadow input 静默失败）
```

### 查找后端元素 backendNodeId 的流程

```javascript
// 1. 获取完整 DOM 树（6MB+）
DOM.getDocument({depth: -1})

// 2. 在返回 JSON 中搜索目标元素的关键属性
// grep 'localFileUploadInp' DOM_output.txt
// 找到行：{"nodeId": 14297, "backendNodeId": 15402, ..., "attributes": ["type","file","id","localFileUploadInp",...]}

// 3. 验证节点类型
DOM.describeNode({backendNodeId: 15402})
// 检查 shadowRoots 是否存在
```

### 相关命令速查

```javascript
// 获取完整 DOM 树
{method: "DOM.getDocument", params: {depth: -1}}

// 验证节点
{method: "DOM.describeNode", params: {backendNodeId: N}}

// 设置文件输入（对 user-agent shadow input 无效）
{method: "DOM.setFileInputFiles", params: {backendNodeId: N, files: ["C:\\path\\to\\file.pdf"]}}

// 拦截文件选择对话框
{method: "Page.setInterceptFileChooserDialog", params: {enabled: true}}
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*