---
name: dxm-packaging
description: 店小秘速卖通编辑页——包装信息模块：包装后重量 + 包装后尺寸（长/宽/高）
domain: ecommerce
triggers:
  - 用户说"包装信息"、"包装后重量"、"包装尺寸"
---

# 店小秘包装信息模块

## 位置

单页面布局，包装信息 section（#packageInfo）在页尾，y≈8200-8500。

切换方式：
```python
await page.evaluate('window.scrollTo(0, 8100)')
# 或
await page.evaluate('document.getElementById("packageInfo").scrollIntoView({block:"start"})')
```

## 字段

| 字段 | 规则 | 来源 | 星号 |
|:--|:--|:--|:--|
| 包装后重量(kg) | 单件重量(kg) | 1688提取(g÷1000) | ⭐ |
| 包装后尺寸 长(cm) | 外包装长 | 1688有则填 | |
| 包装后尺寸 宽(cm) | 外包装宽 | 1688有则填 | |
| 包装后尺寸 高(cm) | 外包装高 | 1688有则填 | |

## 操作

### 包装后重量

```python
# Playwright 方式（推荐）
weight_input = page.locator('.ant-form-item').filter(has_text='包装后重量').locator('input[type="text"]').first
await weight_input.fill('0.2')

# JS fallback（备选）
await page.evaluate('''() => {
    const items = document.querySelectorAll('.ant-form-item');
    for (const item of items) {
        const label = item.querySelector('label');
        if (label && label.textContent.includes('包装后重量')) {
            const inp = item.querySelector('input[type="text"]');
            if (inp) {
                const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                setter.call(inp, '0.2');
                inp.dispatchEvent(new Event('input', {bubbles: true}));
                inp.dispatchEvent(new Event('change', {bubbles: true}));
                inp.dispatchEvent(new Event('blur', {bubbles: true}));
            }
        }
    }
}''')
```

### 包装后尺寸

1688无数据 → 跳过。三格（长/宽/高），位置相邻。

## ⚠️ 已知坑点
1. 包装后尺寸无1688数据 → 跳过不填
2. 重量有"自定义计重"checkbox (type=checkbox)，不要误填到它
3. triple-click+type 对此输入框无效 → 用 `page.fill()` 或 `nativeValueSetter`

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*