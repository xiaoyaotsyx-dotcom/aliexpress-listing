---
name: dxm-qa-check
description: 店小秘速卖通上品——QA复核模块：逐字段校验1688数据准确性、星号必填项、定价公式、关键字段完整度
domain: ecommerce
triggers:
  - 用户说"检查"、"复核"、"QA"、"审核"、"验证"
  - 上品流程最后一步
---

# 店小秘上品QA检查模块

## 触发时机

所有模块(1-9)填完后、保存前，自动执行。

## 检查维度

### 1. 1688 数据准确性 ⭐最关键

| 检查项 | 1688来源 | 页面值 | 规则 |
|:--|:--|:--|:--|
| 成本价 | 1688详情页 | N/A(不填到页面) | 用于验算零售价 |
| 重量(g) | 1688参数表 | 包装后重量(kg) | g÷1000=kg |
| 库存 | 1688规格行 | SKU库存 | >2000封顶2000 |
| 材质 | 1688参数表 | 属性→材质 | 选最接近 |
| 品牌 | 1688参数表 | 属性→品牌 | NONE或实际 |
| 产地 | 1688参数表 | 属性→产地 | 中国大陆+省份 |

### 2. 定价公式验算

```
零售价 = (1688成本价 + 5) × 1.02 ÷ 0.413
       = (成本 + 5) × 2.469

验证：零售价 ≤ 页面值 ± 0.01
货值 = 零售价（两列同值）
```

### 3. 星号字段全覆盖 ⭐提交失败主因

逐模块检查所有 `ant-form-item-required` 字段:

| 模块 | 必填项 | 检查方式 |
|:--|:--|:--|
| 基本信息 | 标题、分类 | 标题无中文、分类已选 |
| 属性信息 | 产地/品牌/液晶/出餐量/材质/智能/化学品/电池 | 全部非空 |
| 产品信息 | 图片/计件单位/容量/SKU定价(全部) | 6张主图、SKU全填 |
| 描述信息 | PC端描述 | 有内容、图已翻译 |
| 包装信息 | 包装后重量 | 非空 |
| 模板信息 | 运费/服务/海关 | 非"请选择" |
| 其他信息 | 报价含关税 | 非空 |

### 4. 关键字段一致性

| 检查 | 说明 |
|:--|:--|
| Green/Pink行一致 | 零售价/货值/库存/重量/原箱/物流 两行完全相同 |
| 是否原箱=是 | select value='1' |
| 物流属性=普货 | 无电池产品 |
| 商品编码 | Green/Pink 已生成 |
| 图片翻译 | 主图6张+SKU图+PC描述图 全部提交 |

## 执行方法

### 🥇 首选：execute_code + websocket CDP 全页扫描（2026-07-19新增）

`browser_snapshot` 输出在 ~1500 行截断，无法覆盖编辑页下半部分。**替代方案：** 用 `execute_code` + websocket 直连 CDP relay 进行全页 QA 扫描。

详见 `aliexpress-store-ops` → `references/cdp-websocket-qa-scan.md`

```python
import asyncio, json
import websockets

async def qa():
    ws = await websockets.connect("ws://127.0.0.1:19223/devtools/page/{targetId}", max_size=None)
    msg = {"id": 1, "method": "Runtime.evaluate", "params": {"expression": """
    (() => {
        const body = document.body.innerText;
        return JSON.stringify({
            chineseError: body.includes('中文字符'),
            pleaseSelectCount: (body.match(/请选择/g) || []).length,
            bodyLength: body.length
        });
    })()
    """, "returnByValue": True}}
    await ws.send(json.dumps(msg))
    resp = await asyncio.wait_for(ws.recv(), timeout=10)
    return json.loads(resp)
```

**targetId 获取：** `curl -s http://127.0.0.1:19223/json` → 找 `dianxiaomi.com/web/smt/edit` 的 target

### 备选：批量星号检查（DOM查询，可能误判）

### 批量星号检查
```python
star_report = await page.evaluate('''() => {
    const items = document.querySelectorAll('.ant-form-item');
    const missing = [];
    items.forEach(item => {
        const star = item.querySelector('.ant-form-item-required, [class*="required"]');
        if (!star) return;
        const label = item.querySelector('label');
        const inp = item.querySelector('input');
        const sel = item.querySelector('.ant-select-selector');
        const val = inp ? inp.value : (sel ? sel.textContent.trim() : '?');
        const isEmpty = !val || val.includes('请选择') || val.includes('请选中');
        if (isEmpty) {
            missing.push((label?.textContent || '?').trim());
        }
    });
    return missing;
}''')
# missing 为空 → 全部星号已填 ✅
```

### 定价公式验算
```python
cost = 1688成本价
expected = round((cost + 5) * 1.02 / 0.413, 2)
actual = float(page输入框中的零售价)
assert abs(expected - actual) < 0.02, f"定价异常: 预期{expected} 实际{actual}"
```

### SKU两行一致性
```python
green = {零售价, 货值, 库存, 重量, 原箱, 物流}
pink = {同上}
assert green == pink, "SKU两行不一致!"
```

## 报告格式

```
📋 QA检查报告
━━━━━━━━━━━━━━━━
✅ 1688数据准确性: 通过
✅ 定价公式: 15.56 = (1.30+5)×2.469 ✓
✅ 星号字段: 全部已填 (0个缺失)
✅ SKU一致性: Green=Pink ✓
✅ 图片翻译: 全部提交
✅ 模板: 运费/服务已选
━━━━━━━━━━━━━━━━
结论: 可以保存
```

## ⚠️ 常见问题
1. 最小出餐量容易漏填 —— 1688无数据也要选一个值
2. Pink行SKU未更新 —— 用nth(2)不是nth(1)
3. 图片改尺寸后未翻译 —— 检查每个section的翻译提交状态
4. 包装尺寸无1688数据 —— 跳过，不算缺失
5. 非星号字段（电源/电压/动力等）所有自动化方法无法选中 —— 已确认的 Vue 3 免疫字段，跳过不纠缠，汇报给用户手动操作

## 🚨 QA误判陷阱（2026-07-19新增）—— 已填字段被误报为"缺失"

**问题：** 用 DOM 元素检查法（`.ant-select-selection-item`、`.ant-form-item` input）会漏读已填值，产生大量误报。

**根因：** 
- `ant-select-auto-complete` 型字段值存储在 `input.value` 中，不在 `.ant-select-selection-item` 的 `.textContent` 中
- 部分 ant-select 选中值通过嵌套 `<div>` 渲染，`.textContent` 可能返回空/空白
- Vue 3 响应式更新后 DOM 结构可能与预期不同

**正确验证方法（按优先级）：**
1. **页面 body 全文搜索（最可靠）：** `document.body.innerText.includes('Plastic')` 等 —— 只要值在页面上任何地方渲染，就能匹配
2. **按字段类型分别读取：**
   - 普通 ant-select：`'.ant-select-selection-item'` 的 `.textContent.trim()`
   - auto-complete 型（材质/最大出餐量等）：`.ant-select-auto-complete input` 的 `.value`
   - 原生 input：`input.value`
3. **不要只依赖一种读取方式** —— 如果 DOM 读不到但 body 文本有值，以 body 文本为准

**误报处理规则：**
- 如果 body 文本能找到值 → 字段已填 ✅，不要重新操作
- 只有在 body 文本中也找不到值时才标记为真正缺失 ❌
- 向用户汇报时先筛掉误报，只报告真正缺失的字段

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*