# 1688数据提取 — 嵌入JSON法（2026-07-13 新增）

当1688页面被重定向到登录页时，产品数据仍在HTML嵌入的JSON中。

## 代码模式

```python
new_page = await browser.contexts[0].new_page()
await new_page.goto('https://detail.1688.com/offer/{offer_id}.html', timeout=30000)
await asyncio.sleep(3)

info = await new_page.evaluate("""
() => {
    const t = document.body.textContent;
    return {
        price: t.match(/"price":"([\d.]+)"/)?.[1],
        weight: t.match(/"skuWeight":\{[^}]*?(\d+\.\d+)/)?.[1],
        material: t.match(/"材质","values":\["([^"]+)"\]/)?.[1],
        brand: t.match(/"品牌","values":\["([^"]+)"\]/)?.[1],
        title: t.match(/"subject":"([^"]+)"/)?.[1]
    };
}
""")
```

## 提取的字段

| 字段 | 正则 | 备注 |
|:--|:--|:--|
| `price` | `/"price":"([\d.]+)"/` | SKU表零售价=货值 |
| `weight` | `/"skuWeight":\{[^}]*?(\d+\.\d+)/` | SKU表重量(kg) |
| `material` | `/"材质","values":\["([^"]+)"\]/` | 属性→材质 |
| `brand` | `/"品牌","values":\["([^"]+)"\]/` | 属性→品牌 |
| `title` | `/"subject":"([^"]+)"/` | 产品标题 |
| `货号` | 文本前后行 `「货号」下一行` | 商品编码前缀 |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*