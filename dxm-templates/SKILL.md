---
name: dxm-templates
description: 店小秘速卖通编辑页——模板信息模块：运费模板 + 服务模板 + 海关监管属性
domain: ecommerce
triggers:
  - 用户说"模板信息"、"运费模板"、"服务模板"、"海关监管"
---

# 店小秘模板信息模块

## 位置

单页面布局，#templateInfo section 在 y≈8466。

```python
await page.evaluate('window.scrollTo(0, 8100)')
```

## 字段

| 字段 | 类型 | 操作 | 星号 |
|:--|:--|:--|:--|
| 运费模板 | ant-select | 选预设模板 | ⭐ |
| 服务模板 | ant-select | 选预设模板 | ⭐ |
| 海关监管属性 | 已填(默认) | 通常预设值=3 | ⭐ |

## 操作

### ant-select 选择（Playwright mouse.click 方式）

```python
# 获取selector坐标
sel = await page.evaluate('''() => {
    const section = document.getElementById('templateInfo');
    const items = section.querySelectorAll('.ant-form-item');
    for (const item of items) {
        const label = item.querySelector('label');
        if (label && label.textContent.includes('运费模板')) {
            const s = item.querySelector('.ant-select-selector');
            const r = s.getBoundingClientRect();
            return {x: r.x+r.width/2, y: r.y+r.height/2};
        }
    }
    return null;
}''')

# 点开下拉
await page.mouse.click(sel['x'], sel['y'])
await asyncio.sleep(1)

# 找可见选项
opts = await page.evaluate('''() => {
    return [...document.querySelectorAll('.ant-select-item-option')]
        .filter(i => i.getBoundingClientRect().height > 0)
        .map(i => ({text: i.textContent.trim(), x: ..., y: ...}));
}''')

# 点第一个（默认）选项
await page.mouse.click(opts[0]['x'], opts[0]['y'])
```

## 选值规则

| 字段 | 推荐选择 |
|:--|:--|
| 运费模板 | 根据零售价选：<$5→"2-5美金 2kg以下"，$5-8→对应档位 |
| 服务模板 | "Service Template for New Sellers"（通常唯一选项） |
| 海关监管属性 | 默认值=3，无需修改 |

## ⚠️ 已知坑点
1. 海关监管属性是 `<input type="text">` 不是 select，值=3 已预设
2. 服务模板通常只有1个选项
3. ant-select 用 `page.mouse.click()` 打开，`.ant-select-item-option` 可见后点击
4. 每选完一个后要等下拉关闭再操作下一个

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*