---
name: dxm-sku-pricing
description: 店小秘速卖通编辑页——SKU定价栏模块：零售价/货值/库存/重量/尺寸/是否原箱/物流属性/商品编码，含定价公式
domain: ecommerce
triggers:
  - 用户说"SKU"、"定价栏"、"零售价"、"货值"、"物流属性"、"商品编码"、"原箱"、"填充SKU"
  - 店小秘编辑页产品信息 tab 需要填SKU表
---

# 店小秘SKU定价栏模块

## 环境

CDP browser_cdp 直连。

## 切换位置

SKU表在「产品信息」tab 的下方，颜色SKU配置区域之后。

## 字段规则速查

| 字段 | 规则 |
|:--|:--|
| **零售价(CNY)** | = 货值，由定价公式计算。≠1688成本价！ |
| **货值(CNY)** | = 零售价，两列填同一个数 |
| **库存** | 1688库存>2000封顶2000，≤2000如实写 |
| **重量(kg)** | 从1688提取 |
| **包装尺寸(cm)** | 长/宽/高，1688有则填，无跳过 |
| **是否原箱** | 原生`<select>`，设为「是」(value=1) |
| **物流属性** | 无电→普货；有电→内电（选具体电池类型） |
| **商品编码** | 一键生成，1688有货号则填为前缀 |

## 💲 定价公式

```
零售价 = 货值 = (1688成本价 + 国内运费¥5) × 1.02 ÷ [0.70 × (1 - 21% - 净利率)]
```

### 费率说明
- 1.02 = 退货率 2%
- 0.70 = (1 - 平台费率 30%)
- 21% = 其他费率 (10% + 3% + 8%)
- 净利率：起量/引流款=20%, 利润款=30%, 新品=20%

### 快速计算（净利率20%）
```
零售价 = (成本 + 5) × 1.02 ÷ 0.413
       = (成本 + 5) × 2.469
```

## Step 8a：逐行填写 SKU 值（✅ 2026-07-19 验证）

### 🔑 Playwright `page.locator().fill()` — 唯一可靠方式

店小秘 SKU 表的 antd input 不能用 triple-click+keyboard.type 或 nativeValueSetter 填值。**唯一可靠方式：Playwright `page.locator('input[placeholder="字段名"]').fill('值')`**。

```python
# 零售价 (SKU 1 = nth(0), SKU 2 = nth(2)! 跳过 nth(1) 隐藏行)
await page.locator('input[placeholder="零售价"]').nth(0).fill('15.56')  # SKU 1 (Green)
await page.locator('input[placeholder="零售价"]').nth(2).fill('15.56')  # SKU 2 (Pink)

# 货值（同零售价）
await page.locator('input[placeholder="货值"]').nth(0).fill('15.56')
await page.locator('input[placeholder="货值"]').nth(2).fill('15.56')

# 库存
await page.locator('input[placeholder="库存"]').nth(0).fill('2000')
await page.locator('input[placeholder="库存"]').nth(2).fill('2000')

# 重量
await page.locator('input[placeholder="重量"]').nth(0).fill('0.2')
await page.locator('input[placeholder="重量"]').nth(2).fill('0.2')
```

### ⚠️ 注意
- 每个 placeholder 可能有 3 个匹配——**`nth(0)` 是第 1 个 SKU，`nth(2)` 是第 2 个 SKU！`nth(1)` 是隐藏/批量行，不要填它！**
- 填值前先 `nth(i).click()` 聚焦，再 `.fill(value)`
- 不需要 `dispatchEvent` — Playwright fill 会自动触发 Vue 3 响应
- **填完后立即验证**：用逐行读表方式确认两个 SKU 的值一致（避免只改了第 1 行没改第 2 行）

### ❌ 已证伪的方法
- triple-click + keyboard.type — 值不持久化
- nativeValueSetter + dispatchEvent — Vue 3 不认
- 表头「批量填充」按钮 → 不适用逐行不同值的场景（两个颜色 SKU 价格相同可尝试）

## Step 8b：是否原箱

### 使用原生 `<select>`，不是 ant-select！

```python
# Playwright select_option（推荐）
selects = page.locator('table select')
for i in range(selects.count()):
    opts = await selects.nth(i).locator('option').all_inner_texts()
    if '是' in opts:
        await selects.nth(i).select_option(value='1')  # 1 = 是

# JS fallback（备选）
await page.evaluate('''() => {
    const selects = document.querySelectorAll('table select');
    for (const sel of selects) {
        if (sel.options.length >= 3 && sel.options[2].text === '是') {
            sel.selectedIndex = 2;
            sel.dispatchEvent(new Event('change', {bubbles: true}));
        }
    }
}''')
```

⚠️ 第一个 select（i=0）通常是颜色筛选器，跳过它。只改 是否原箱 的 select。
⚠️ Playwright `select_option` 是原生 select 的最可靠方式。

## Step 8c：物流属性（✅ 2026-07-19 验证）

### 判断规则
| 产品类型 | 物流属性 |
|:--|:--|
| 无电（硅胶碗、普通日用品） | **普货** |
| USB充电（风扇、净化器） | 内电→非纽扣锂离子电池 |
| 纽扣电池（LED灯） | 内电→纽扣式锂电池 |
| 干电池（遥控器） | 内电→干电池 |
| 充电宝/电池盒 | 内电→非纽扣锂离子电池 |

### CDP 操作（Playwright）

```
1. 找物流属性列 header 中的「批量」span
   th_textContent_contains('物流属性') → querySelector('span') → 文字为'批量'
   坐标约 (1778, 709)（scroll 后可能变化，每次实时查询）

2. page.mouse.click(x, y) 打开弹窗
   弹窗结构：
     物流属性
     禁运: 禁运
     普货: 普货          ← 选这个
     纯电: 纯电
     强磁: 强磁
     特货: 液体/粉末/膏体/特货其他
     特敏: 危险品/特敏其他
     内电: 干电池/铅酸蓄电池/.../非纽扣锂离子电池
     外电: 外电
     弱磁: 弱磁
     [取消] [确定]

3. 选对应 checkbox
   page.mouse.click(普货_label_x, 普货_label_y)  // 约 (790, 232)

4. 点「确定」
   page.mouse.click(确定_btn_x, 确定_btn_y)  // 约 (1466, 842)
```

### ⚠️ 注意
- 弹窗按钮坐标每次弹窗位置固定，但建议实时 `getBoundingClientRect()` 获取
- mouse.click 在此弹窗中有效（不是所有 ant-modal-wrap 都拦截点击）

## Step 8d：商品编码（✅ 2026-07-19 验证）

### 必须先设物流属性！否则报错。

```
1. 点 header 中的「一键生成」span（约 1899, 710）
   page.mouse.click(1899, 710)

2. 弹窗「商品编码 设置」出现
   按钮：[关闭] [设置]

3. 点「设置」自动生成（约 1213, 164）
   page.mouse.click(1213, 164)

4. 弹窗关闭 → 每个 SKU 行商品编码自动填入（值如 'Green' / 'Pink'）
```

### ⚠️ 注意
- 不需要填前缀或手动输入——点「设置」即自动生成
- 生成结果是 SKU 自定义名称（如 Green/Pink），非 1688 货号
- 如有 1688 货号（如 BK），可在弹窗中自行修改前缀

## Step 0：获取 1688 成本价（前置条件）

### 来源URL查找优先级
1. **编辑页 DOM**：搜索所有含 `1688.com` 的 a 链接 / innerText
2. **店小秘信息 tab**：切到「店小秘信息」→ 找来源URL
3. **🔴 浏览器直接搜索（推荐兜底）**：在已登录1688的Chrome中新标签页搜索产品标题 → 从搜索结果找到对应产品 → 点进详情页 → 提取价格和参数
4. **会话历史**：用 `session_search` 搜产品标题 + "1688" + "价格"

### 🔑 浏览器搜索1688详细步骤
```
1. 在已有 Chrome CDP 连接中：ctx.new_page()
2. goto('https://s.1688.com/selloffer/offer_search.htm?keywords=产品关键词&n=y')
3. page.evaluate('document.body.innerText') 提取搜索结果
4. 匹配标题最接近的产品，从 innerText 中提取价格（正则：/¥\s*([\d.]+)/）
5. 或直接 page.mouse.click 点进详情页 → goto('https://detail.1688.com/offer/{offer_id}.html')
6. 从详情页 innerText 提取：
   - 价格：¥(\d+\.\d+)
   - 库存：规格行后紧跟的 \d+ 数字
   - 重量：(\d+)g
   - 材质/品牌/产地：表格文本中提取
```

### 🔴 用户期望
**用户明确要求：自己从浏览器中找，不要问用户。** "你自己分辨，你不要问我，好吗？我们都已经上架了，你刚才在编辑那个页面，那个页面上也有网页链接，有采集的产品的链接，你自己去学习，自己去研究。"
→ 优先用浏览器搜索1688找到产品并提取价格，实在找不到（如1688需验证码/登录失效）时再问。

### 常见失败原因
- 店小秘采集箱产品不保留原始1688 URL
- 1688 搜索触发验证码 → 等用户手动通过后再操作
- 1688 未登录 → 搜索页会跳转到登录页，请用户登录后再试

## ⚠️ 已知坑点
1. 「零售价 = 货值，不等于1688成本价」— 经常搞反
2. 是否原箱用原生 `<select>`，第一个 select 是颜色筛选器要跳过
3. 商品编码必须先设物流属性
4. 库存封顶2000
5. 国内运费固定¥5，不是0
6. 用户说「是否原籍」= 是否原箱（语音识别）
7. **1688成本价优先自己找** — 不要在第一步就问用户，先尝试浏览器搜索
8. **🔑 使用 `page.locator('input[placeholder="..."]').fill()`** — 这是填 antd 表 input 的唯一可靠方式。triple-click+keyboard 和 nativeValueSetter 均无效。
9. **SKU 表每个 placeholder 有 3 个匹配——nth(0)=第1个SKU, nth(2)=第2个SKU, nth(1)=隐藏行（不要填！）**
10. **物流属性弹窗中 mouse.click 有效** — 不触发 ant-modal-wrap 拦截问题
11. **填完必须逐行验证** — 否则可能出现只改了第 1 行、第 2 行还是旧值的情况，用户会看到两个 SKU 价格不一致。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*