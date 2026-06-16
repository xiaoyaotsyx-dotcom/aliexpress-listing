# CDP 鼠标事件技术 — 店小秘 Ant Design Dropdown 绕过

> 2026-06-15 发现并验证。适用于所有 Ant Design Dropdown 在 CDP 模式下 JS click 不生效的场景。

## 问题

Hermes browser 模式下，以下元素通过 JS `.click()` 无法打开：
- Ant Design Dropdown Button（上传文件菜单）
- Ant Design Select 下拉（某些情况下）
- 任何 `.ant-dropdown-trigger` 组件

React 事件绑定监听的是浏览器原生鼠标事件，JS 模拟的 `.click()` 不会触发。

## 解决方案

通过 CDP `Input.dispatchMouseEvent` 发送真实鼠标事件。

### 通用代码模板

```python
import asyncio
import websockets
import json
import aiohttp

async def cdp_click_element(page_url, selector_or_text):
    """通过 CDP 鼠标事件点击元素"""
    async with websockets.connect(page_url, max_size=5*1024*1024) as ws:
        mid = 1
        
        # 1. 获取元素在视口中的坐标
        await ws.send(json.dumps({
            "id": mid, "method": "Runtime.evaluate",
            "params": {
                "expression": f"""
                    var el = {selector_or_text};
                    if (!el) {{ JSON.stringify({{found: false}}); }}
                    var r = el.getBoundingClientRect();
                    JSON.stringify({{x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2), found: true}});
                """,
                "returnByValue": True
            }
        }))
        while True:
            raw = await ws.recv()
            resp = json.loads(raw)
            if resp.get("id") == mid:
                coord = json.loads(resp['result']['result']['value'])
                break
        
        if not coord.get("found"):
            return {"error": "element not found"}
        
        # 2. 点击（mousePressed + mouseReleased）
        for action in ["mousePressed", "mouseReleased"]:
            mid += 1
            await ws.send(json.dumps({
                "id": mid, "method": "Input.dispatchMouseEvent",
                "params": {
                    "type": action,
                    "x": coord["x"],
                    "y": coord["y"],
                    "button": "left",
                    "clickCount": 1
                }
            }))
            await ws.recv()
        
        return {"clicked": True, "x": coord["x"], "y": coord["y"]}

async def main():
    # 获取页面的 WebSocket URL
    async with aiohttp.ClientSession() as session:
        async with session.get("http://172.24.48.1:9255/json") as resp:
            pages = await resp.json()
    
    # 找到店小秘编辑页
    page_url = None
    for p in pages:
        if "dianxiaomi" in p.get("url", "") and "edit" in p.get("url", ""):
            page_url = p["webSocketDebuggerUrl"]
            break
    
    if not page_url:
        print("No 店小秘编辑页 found")
        return
    
    # 示例：点击"上传文件"按钮
    result = await cdp_click_element(page_url, 
        "[...document.querySelectorAll('button')].find(b => b.textContent.includes('上传文件'))")
    print(result)

asyncio.run(main())
```

### 选择下拉选项

点击打开下拉后，等待 600-800ms，然后点击菜单项：

```python
await asyncio.sleep(0.8)

# 查看可见的菜单项
await ws.send(json.dumps({
    "id": mid, "method": "Runtime.evaluate",
    "params": {
        "expression": """
            var items = document.querySelectorAll('.ant-dropdown-menu-item');
            JSON.stringify(Array.from(items).filter(i => i.offsetParent !== null).map(i => i.textContent.trim()));
        """,
        "returnByValue": True
    }
}))

# 点击目标选项
# 用同样的 cdp_click_element 方法点击可见的菜单项
```

## 适用场景

| 场景 | 选择器 | 说明 |
|:--|:--|:--|
| 上传文件菜单 | `[...document.querySelectorAll('button')].find(b => b.textContent.includes('上传文件'))` | 打开本地上传/图片空间/URL链接菜单 |
| 产品名下拉 | `document.querySelector('.ant-modal .ant-select-selector')` | 海关监管弹窗中的品名选择 |
| 运费模板 | `[...document.querySelectorAll('.ant-select-selector')].find(s => s.textContent.includes('请选择运费模板'))` | 运费模板下拉 |

## 替代方案

如果 CDP 鼠标事件也不生效，尝试以下方案：

1. **`DOM.setFileInputFiles`** — 用于文件上传，直接设置隐藏 `#localFileUploadInp` 的值
2. **`Runtime.evaluate` 直接操作 React 状态** — 极端情况（不推荐）

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*