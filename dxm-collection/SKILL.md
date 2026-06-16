---
name: dxm-collection
description: 速卖通上架——1688采集模块：从1688搜索产品 → 采集到店小秘采集箱 → 提取产品参数（价格/库存/重量/材质等）
domain: ecommerce
triggers:
  - 用户说"采集"、"从1688采集"、"搜1688"、"1688参数"
  - 需要从1688获取产品成本价和规格参数
---

# 1688采集模块

## 流程总览

```
店小秘采集箱 → 点「采集数据」→ 搜1688关键词 → 
找到产品 → 采集 → 回到采集箱 → 产品已入列表
```

## Step 1：进入采集箱

URL：`https://www.dianxiaomi.com/web/smt/smtProductList/draft`

左侧菜单：产品 → 采集箱 → 速卖通采集箱

## Step 2：采集1688产品

点击「采集数据」按钮 → 弹窗 → 搜索1688关键词 → 找到目标产品 → 点「采集」

## Step 3：提取1688参数

### 3a：获取1688 URL（不要点「访问」按钮！）

```python
url = await page.evaluate("""
  document.querySelector('input[value*="1688.com"]')?.value
""")
# 新标签页打开
new_page = await browser.contexts[0].new_page()
await new_page.goto(url)
```

### 3b：提取参数

路径1：页面innerText正则提取
- 成本价：`/¥\s*([\d.]+)/`（≥2件起批价）
- 库存：规格行后紧跟数字
- 重量：`(\d+)g` → ÷1000 = kg
- 材质/品牌/货号：参数表格文本

路径2：嵌入JSON（如果有）：`window.__INIT_DATA__`

### 3c：1688搜索（URL未知时）

```python
search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={keyword}&n=y"
```

## 参数映射

| 1688 | 店小秘 | 规则 |
|------|--------|------|
| 价格 | 成本价 | 直接用 |
| 库存 | 库存 | >2000封顶2000 |
| 重量g | 重量kg | ÷1000 |
| 材质 | 材质 | 硅胶→Plastic |
| 品牌 | NONE | 无授权 |
| 货号 | 编码前缀 | 编码弹窗中填 |

## ⚠️ 坑点

1. 编辑页「访问」按钮会覆盖编辑页 → 必须JS读URL + 新标签页
2. 1688需登录，未登录价格隐藏
3. 可能触发验证码
4. 价格取≥2件起批价

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*