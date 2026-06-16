# 1688 参数访问工作流

## 场景
从店小秘编辑页的「店小秘信息」→「来源URL」查看 1688 产品参数。

## 🔴 铁律
**不能点击页面上的「访问」按钮！** Hermes `browser_click` 点击「访问」按钮可能导致当前编辑页被导航到 1688 页面，导致所有已填数据丢失。

## 正确操作

### 方式1：Playwright 新标签页（推荐）
```python
alibaba_url = await edit_page.evaluate("""
    () => {
        var inputs = document.querySelectorAll('input');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].value && inputs[i].value.includes('detail.1688.com')) {
                return inputs[i].value;
            }
        }
        return null;
    }
""")
new_tab = await ctx.new_page()
await new_tab.goto(alibaba_url, wait_until='domcontentloaded')

info = await new_tab.evaluate("""
    () => {
        var t = document.body.textContent || '';
        return {
            price: t.match(/"price":"([0-9.]+)"/)?.[1],
            brand: t.match(/"品牌","values":\["([^"]+)"\]/)?.[1],
            material: t.match(/"材质","values":\["([^"]+)"\]/)?.[1],
            weight: t.match(/"skuWeight":\{[^}]*?(\\d+\\.\\d+)/)?.[1],
            origin: t.match(/"产地","values":\["([^"]+)"\]/)?.[1],
            stocks: [...t.matchAll(/"canBookCount":(\\d+)/g)].map(m => m[1])
        };
    }
""")
```

### 方式2：复用已有 1688 标签页
```python
for pg in ctx.pages:
    if '1688.com/offer' in pg.url:
        info = await pg.evaluate("""...""")
```

## ⚠️ 重量陷阱
JSON 的 `skuWeight` 字段（如 `0.2000`）**不可靠**。以页面规格表的 **重量(g)** 列为准。

## 可提取字段映射
| 字段 | 正则 | 填写 |
|:--|:--|:--|
| price | `/"price":"([0-9.]+)"/` | SKU零售价=货值 |
| 品牌 | `/"品牌","values":\["([^"]+)"\]/` | NONE |
| 材质 | `/"材质","values":\["([^"]+)"\]/` | 对应值 |
| weight | `/"skuWeight":\{[^}]*?(\d+\.\d+)/` | SKU重量(kg) |
| 产地 | `/"产地","values":\["([^"]+)"\]/` | 中国大陆 |
| canBookCount | `/"canBookCount":(\d+)/g` | 库存封顶2000 |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*