# Playwright 坐标点击法 — ant-select 下拉填充

## 背景

CDP `Input.dispatchMouseEvent` 有时无法可靠触发 Vue 3 的事件处理。Playwright `connect_over_cdp()` + `page.mouse.click(x, y)` 通过真实坐标点击能穿透 Vue 响应式系统。

## 前置条件

CDP relay 链必须正常：
```
Chrome (127.0.0.1:9222) → Relay2.exe (0.0.0.0:9255) → WSL chrome_relay.py (127.0.0.1:19223)
```

验证：`curl -s http://127.0.0.1:19223/json/version` 返回 200。

## 核心模式

```python
import asyncio
from playwright.async_api import async_playwright

async def fill_ant_select(page, select_index, target_text):
    """填充一个ant-select：坐标点击打开 → 坐标点击选值"""
    
    # 0. 强制隐藏所有残留下拉
    await page.evaluate("""
        document.querySelectorAll('.ant-select-dropdown').forEach(dd => 
            dd.classList.add('ant-select-dropdown-hidden'))
    """)
    
    # 1. 滚动到可见区域
    await page.evaluate(f"""
        document.querySelectorAll('#attrInfo .ant-select')[{select_index}]
            .scrollIntoView({{block: 'center'}})
    """)
    await asyncio.sleep(0.3)
    
    # 2. 获取坐标并点击打开下拉
    rect = await page.evaluate(f"""
        (() => {{
            const el = document.querySelectorAll('#attrInfo .ant-select')[{select_index}];
            const r = el.getBoundingClientRect();
            return {{x: r.x + r.width/2, y: r.y + r.height/2}};
        }})()
    """)
    await page.mouse.click(rect['x'], rect['y'])
    await asyncio.sleep(1.0)
    
    # 3. 读可用选项
    options = await page.evaluate("""
        Array.from(document.querySelectorAll(
            '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option'
        )).filter(i => i.offsetParent !== null).map(i => i.textContent.trim())
    """)
    
    # 4. 匹配目标
    if target_text not in options:
        # 尝试部分匹配
        match = next((o for o in options if target_text.split('(')[0] in o), None)
        target_text = match or options[0]
    
    # 5. 获取选项坐标并点击
    coords = await page.evaluate(f"""
        (() => {{
            const items = document.querySelectorAll(
                '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option'
            );
            for (const item of items) {{
                if (item.textContent.trim() === '{target_text}') {{
                    const r = item.getBoundingClientRect();
                    return {{x: r.x + r.width/2, y: r.y + r.height/2}};
                }}
            }}
            return null;
        }})()
    """)
    if coords:
        await page.mouse.click(coords['x'], coords['y'])
    return target_text
```

## 批量填充示例

```python
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:19223')
        page = browser.contexts[0].pages[0]  # 确保是编辑页
        
        fields = [
            (3, '无(No)'),      # 液晶显示
            (4, '500g(500g)'),  # 最大出餐量
            (5, '100g(100g)'),  # 最小出餐量
            (7, 'no(no)'),      # 是否智能
            (9, 'no(no)'),      # 是否包含电池
        ]
        
        for idx, target in fields:
            result = await fill_ant_select(page, idx, target)
            print(f"[{idx}] → {result}")
```

## ⚠️ 常见故障

| 故障 | 原因 | 解决 |
|:--|:--|:--|
| 下拉不出现 | 残留下拉拦截 | `classList.add('ant-select-dropdown-hidden')` 强制隐藏 |
| 选项列表为空 | 搜索型select需要输入 | 先点开搜索框或直接 `.ant-select-selector` 而非 `.ant-select` |
| Playwright连接超时 | CDP relay断了 | 执行CDP恢复流程（参考 `cdp-recovery.md`） |
| `mouse.click` 报 intercept | 前一个下拉遮罩残留 | 先 Escape + JS隐藏所有dropdown |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*