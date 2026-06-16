# CDP 鼠标事件操作参考

Hermes CDP 模式下，React/Ant Design 组件对 JS programmatic `.click()` 无响应时，必须用真实鼠标事件。

## 通过 Hermes browser_console 发送

```javascript
// 获取目标元素坐标
(function() {
    const btn = [...document.querySelectorAll('button')]
        .find(b => b.textContent.includes('目标文字'));
    const r = btn.getBoundingClientRect();
    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
})();
```

如果元素在视口外（`y` 负值），先点击对应的 tab 导航或 `scrollIntoView()`。

## 通过 CDP WebSocket 直接发送（execute_code + python）

```python
import asyncio, websockets, json, aiohttp

async def click_page(x, y):
    async with aiohttp.ClientSession() as session:
        async with session.get("http://172.24.48.1:9255/json") as resp:
            pages = await resp.json()
    
    page_url = None
    for p in pages:
        if "dianxiaomi" in p.get("url", "") and "edit" in p.get("url", ""):
            page_url = p["webSocketDebuggerUrl"]
            break
    
    async with websockets.connect(page_url, max_size=5*1024*1024) as ws:
        mid = 1
        await ws.send(json.dumps({
            "id": mid, "method": "Input.dispatchMouseEvent",
            "params": {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1}
        }))
        await ws.recv()
        mid += 1
        await ws.send(json.dumps({
            "id": mid, "method": "Input.dispatchMouseEvent",
            "params": {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1}
        }))
        await ws.recv()

asyncio.run(click_page(x, y))
```

## 通过 Hermes CDP tool（browser_cdp）

```json
// Step 1: mouse down
{"method": "Input.dispatchMouseEvent", "params": {"type": "mousePressed", "x": X, "y": Y, "button": "left", "clickCount": 1}}

// Step 2: mouse up
{"method": "Input.dispatchMouseEvent", "params": {"type": "mouseReleased", "x": X, "y": Y, "button": "left", "clickCount": 1}}
```

## ⚠️ 致命坑：antd dropdown 绝对定位偏移

**现象：** 用 `Input.dispatchMouseEvent` 点击 `.ant-dropdown-trigger` 后，ant-dropdown 的 `display` 变为 `block`，但 `getBoundingClientRect()` 返回全零/空数组——下拉菜单被渲染到**视口之外**。

**原因：** Ant Design 使用 `style: top: 5612px` 的绝对定位渲染下拉。当触发按钮靠近视口底部时，antd 将下拉放在页面坐标的 xxxxpx 位置，而这个位置在当前视口外。

**修复：** 点按钮之前，先滚动页面让按钮位于视口中部（y≈400-700）。

```javascript
// ✅ 正确做法
// 1. 滚动到按钮在视口适中位置
var r = document.querySelector('.ant-dropdown-trigger').getBoundingClientRect();
window.scrollBy(0, r.top - 400);
// 2. 现在按钮在 y≈400-700，再触发点击
// Input.dispatchMouseEvent(mousePressed) + Input.dispatchMouseEvent(mouseReleased)
```

**验证：**
```javascript
// 点击后检查
var dd = document.querySelector('.ant-dropdown');
var display = getComputedStyle(dd).display;
var rect = dd.getBoundingClientRect();
// display='block' 但 rect={x:0,y:0,w:0,h:0} → 在视口外，需重试
```

## 适用场景

| 组件 | JS .click() | CDP mouse click |
|:--|:--:|:--:|
| Ant Design Button | ✅ | ✅ |
| Ant Design Dropdown (下拉箭头) | ❌ | ✅ |
| Ant Design Select (打开面板) | ✅ (部分版本) | ✅ |
| Native `<button>` | ✅ | ✅ |
| Ant Design Radio (`.ant-radio-wrapper`) | ✅ | ✅ |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*