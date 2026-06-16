# 店小秘属性批量填写 — CDP 坐标操作

> **场景：** Playwright `page.mouse.click()` 对 antd select 无效（dropdown 打开后选项不可点）
> **根本原因：** 店小秘的 Vue 3 + antd 组件在 CDP relay 模式下，Playwright 的事件链不完整。
> **方案：** CDP `Input.dispatchMouseEvent` + `Runtime.evaluate` 组合操作。

## 核心操作流程

每个 antd select 需要两步：

```
Step 1: 找到 selector 坐标 → dispatchMouseEvent(mousePressed+Released) → 打开 dropdown
Step 2: Runtime.evaluate 找到 .ant-select-item-option 匹配文本 → .click() 选中
```

## 前提：滚动到正确位置

antd 的 dropdown 绝对定位从按钮位置向下偏移。如果按钮在视口底部，dropdown 会渲染到视口外（top: 5612px 等）。

```javascript
// 先滚动使属性区在视口中
window.scrollTo(0, 700);  // 根据页面内容调整

// 获取所有未填 selected 的当前坐标
const sels = document.querySelectorAll('.ant-select-selector');
const positions = [];
for (const s of sels) {
  if (s.innerText.trim() !== '请选择') continue;
  const r = s.getBoundingClientRect();
  if (r.top > 0) {
    positions.push({top: r.top + r.height/2, left: r.left + r.width/2});
  }
}
```

## CDP 双击操作模板

```python
# Step 1: 打开 dropdown（左键 click = mousePressed + mouseReleased）
cdp_call({
    "method": "Input.dispatchMouseEvent",
    "params": {"type": "mousePressed", "x": 975, "y": Y, "button": "left", "clickCount": 1},
    "target_id": EDIT_PAGE_TARGET_ID
})
cdp_call({
    "method": "Input.dispatchMouseEvent",
    "params": {"type": "mouseReleased", "x": 975, "y": Y, "button": "left", "clickCount": 1},
    "target_id": EDIT_PAGE_TARGET_ID
})

# Step 2: 选选项（用 Runtime.evaluate 找到并点击）
cdp_call({
    "method": "Runtime.evaluate",
    "params": {
        "expression": "document.querySelector('.ant-select-item-option[title*=\\"浙江\\"]').click()",
        "returnByValue": true
    },
    "target_id": EDIT_PAGE_TARGET_ID
})
```

**说明：**
- `x=975` 是店小秘编辑页右侧区域的固定横坐标（所有属性下拉的 selector 宽度~240px，中点 855+120=975）
- `y` 值随页面滚动变化，每次需重查 `getBoundingClientRect()`
- `clickCount: 1` 不可省略——antd 的 click 事件监听检查 `detail` 属性

## 坐标位置经验值

对应「产品信息」tab 底部区域，scrollTo(0, 700) 后实测：

| 属性 | y坐标(视口) | 目标值 |
|:----|:---------:|:-----:|
| 中国省份(CN) | ~102 | 浙江 |
| 品牌(Brand Name) | ~216 | NONE |
| 高关注化学品 | ~315 | 天然未处理 |
| 品种大小 | ~388 | 所有包装 |
| 类型(Type) | ~446 | 狗狗 |
| 图案类型(Pattern Type) | ~502 | 纯色 |
| 风格(Style) | ~560 | fashion |
| 适应犬种 | ~616 | 通用 |
| 季节(Season) | ~689 | ❌ dropdown 为空 |
| 特性(Feature) | ~745 | ❌ dropdown 为空 |
| 材质(Material) | ~799 | ❌ dropdown 为空 |

**注意：** 这些坐标在页面滚动后会变，必须每次重新查 `getBoundingClientRect()`。

## Playwright 脚本批量操作（已知问题）

```python
# ⚠️ 以下方式在 CDP relay 下经常失败，但值得一试
await page.mouse.click(x, y)
await asyncio.sleep(1.5)
opts = await page.query_selector_all('.ant-select-item-option')
for opt in opts:
    if await opt.is_visible() and '目标值' in await opt.inner_text():
        await opt.click()
        break
```

**常见失败模式：** `is_visible()` 返回 False（元素在 DOM 但 antd 隐藏），或者 dropdown 打开后选项全「EMPTY」。

**推荐方案：** 用 CDP `Input.dispatchMouseEvent`（上面方案）逐个属性操作。

## 狗携带用品类目属性值速查

适用于 狗携带用品(Dog Carriers & Bags) 分类下的便携水壶/折叠碗类产品：

| 属性 | 选什么 | 依据 |
|:----|:------|:----|
| 产地（国家或地区） | 中国大陆 | 1688 产地=义乌 |
| 中国省份(CN) | 浙江 | 义乌在浙江 |
| 产品类型(Item Type) | 饮水器 | 或类似便携水壶选项 |
| 品牌(Brand Name) | NONE | 1688 品牌=斌凯，但速卖通上选无品牌 |
| 高关注化学品 | 天然未处理 | 所有无化学品产品都选这个 |
| 品种大小(Breed size) | 所有包装 | 通用型产品 |
| 类型(Type) | 狗狗 | 面向狗的产品 |
| 图案类型(Pattern Type) | 纯色 | 素色硅胶 |
| 风格(Style) | fashion | 或简约(modern) |
| 适应犬种 | 通用 | 所有犬种 |
| 季节 | ← 下拉空，忽略 |
| 特性 | ← 下拉空，忽略 |
| 材质(Material) | ← 下拉空，可在描述中补充 |
| 承受重量 | ← 下拉空，忽略 |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*