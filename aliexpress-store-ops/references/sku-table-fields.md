# SKU定价栏（用户定义术语）

> **老大定义的统称术语**：店小秘编辑页「产品信息」tab 下 SKU 表中的一整栏定价相关字段。
> 包含：零售价、货值、库存、长/宽/高、是否原箱、物流属性、商品编码。
> 用户说「SKU定价栏」= 一次性处理以上全部字段。

# SKU 表字段位置与填写

## SKU 表格结构

### 表头行（批量填充行）

| 列 | 字段 | 说明 |
|:--|:--|:--|
| 颜色 | 全选/反选 | 勾选后批量设定 |
| 零售价(CNY) | 输入框 | 1688成本价 |
| 货值(CNY) | 输入框 | 同上（零售价=货值） |
| 实际收入 | 自动计算 | 佣金5%后自动算 |
| 批发价 | — | 一般不填 |
| 库存 | 输入框 | 1688数据，>2000封顶 |
| 重量(kg) | 输入框 | 1688参数（g÷1000）|
| 包装尺寸(cm) | 长/宽/高三输入 | 1688数据或用户给 |
| 是否原箱 | 原生select下拉 | 是/否 |
| 物流属性(批量) | 下拉 | 按产品类型 |
| 商品编码 | 输入+一键生成 | 自动或手动 |

### 数据行（每个SKU一行）

每个 SKU 颜色一行（如白色/绿色、黑色/粉色），字段与表头行一致。

## 各字段填写规则

### 零售价 & 货值

**铁律：零售价 = 货值 = 1688成本价**

1688 价格含国内运费 ¥2.2，直接用采集到的价格。

**批量填充方法：**
```python
# 在表头行统一填，点批量填充
inputs = await page.locator('table').nth(11).locator('tr').first.locator('input').all()
values = [retail_price, retail_price, inventory, weight]  # 按列顺序
for i, inp in enumerate(inputs[:4]):
    await inp.click()
    await inp.fill(str(values[i]))
# 点批量填充按钮
await page.get_by_text('批量填充').first.click()
```

### 库存

**规则：** 使用1688原始库存数据。若1688库存>2000则写2000（封顶），若≤2000则如实写。

### 重量(kg)

从1688产品页获取。1688显示的是「重量(g)」，需÷1000转为kg。
例：1688规格列显示「200g」→ 填 0.2

### 包装尺寸(cm)

优先从1688产品页获取（如果有包装信息→商品件重尺）。
若1688无数据，问用户要长/宽/高值。
三个独立输入框（长、宽、高），依次填入。

### 是否原箱（⚠️ CDP 重要坑点）

**字段类型：** 原生 `<select>` 元素（非 ant-select 组件）

```html
<select class="w-full! g-form-component w-full! w-full!">
  <option value="">请选择</option>
  <option value="0">否</option>
  <option value="1">是</option>
</select>
```

**⚠️ 已知问题 — Vue 响应式不被标准化 CDP 事件捕获：**
- ❌ `sel.value = '1'` + `dispatchEvent(new Event('change'))` — Vue 可能不响应
- ❌ `page.evaluate()` 直接设 value — 不被 Vue 响应式系统捕获
- ⚠️ 即使 `select_option()` 后 DOM验证显示已选，用户肉眼观察可能仍显示未选（CDP relay 场景下的已知差异）

**✅ 最佳实践：**
```python
# 方法1：Playwright 原生 select_option（首选）
sel = page.locator('table').nth(11).locator('select').nth(N)
await sel.select_option('1')  # '1' = 是

# 方法2：找所有是否原箱 select 批量设
selects = await page.locator('table').nth(11).locator('select').all()
for sel in selects:
    opts = await sel.locator('option').all()
    vals = [await opt.get_attribute('value') for opt in opts]
    if '' in vals and '0' in vals and '1' in vals:
        await sel.select_option('1')

# 方法3：模拟用户鼠标+键盘
box = await select_el.bounding_box()
await page.mouse.click(box.x + box.w/2, box.y + box.h/2)
await page.keyboard.press('ArrowDown')
await page.keyboard.press('ArrowDown')
await page.keyboard.press('Enter')

# 方法4：用 nativeInputValueSetter（对原生 select 也有效）
# 但需要注意 Vue 可能用 @change 绑定了事件
```

### 物流属性(批量) ⚠️

**不是下拉选择框，是弹窗+checkbox选择器。** 操作方法：

1. 在表头找到「物流属性(批量)」列，点「批量」按钮（`<button>` 在 `<th>` 父元素内）
2. 弹出一个 Ant Design Modal，结构为：
   ```html
   <div class="ant-modal-content">
     <div class="ant-modal-body">
       <div class="logistics-attr-selector">
         <div class="render-container logistics-attr-row">
           <div class="logistics-attr-main">
             <span class="logistics-attr-title">普货:</span>
             <label class="ant-checkbox-wrapper">普货</label>
           </div>
         </div>
         <!-- 其他行类似 -->
       </div>
     </div>
     <div class="ant-modal-footer">
       <button class="ant-btn-default">取消</button>
       <button class="ant-btn-primary">确定</button>
     </div>
   </div>
   ```

3. **选中checkbox：** 直接点 `<label class="ant-checkbox-wrapper">` 即可触发 Ant Design checkbox 状态切换

4. **道具属性分类（由用户指示）：**
   - 无电产品 → **普货**（如硅胶碗、纺织品）
   - 带电产品 → 先查1688 → 选对应**内电**子类（干电池/铅酸蓄电池/镍氢电池/纽扣式锂电池/非纽扣锂金属电池/非纽扣锂离子电池等）
   - 特货 × 4：液体、粉末、膏体、特货其他（互斥）
   - 特敏 × 2：危险品、特敏其他
   - 禁运、纯电、强磁、外电、弱磁各一

5. 点 **确定**（`.ant-btn-primary`，文本为「确定」）确认批量应用

**✅ 最佳实践 Python 代码：**
```python
# 1. 点批量按钮
await page.evaluate('''() => {
    const tables = document.querySelectorAll("table");
    for (let t of tables) {
        const ths = t.querySelectorAll("th");
        for (let th of ths) {
            if (th.textContent.includes("物流属性")) {
                const btn = th.parentElement.querySelector("button");
                if (btn) btn.click();
                return;
            }
        }
    }
}''')
await asyncio.sleep(2)

# 2. 选普货（或其他类型）
await page.evaluate('''() => {
    const modals = document.querySelectorAll(".ant-modal-content");
    for (let modal of modals) {
        if (modal.textContent.includes("物流属性")) {
            const labels = modal.querySelectorAll(".ant-checkbox-wrapper");
            for (let label of labels) {
                if (label.textContent.trim() === "普货") {
                    label.click();
                    break;
                }
            }
            break;
        }
    }
}''')
await asyncio.sleep(1)

# 3. 点确定
await page.evaluate('''() => {
    const modals = document.querySelectorAll(".ant-modal-content");
    for (let modal of modals) {
        if (modal.textContent.includes("物流属性")) {
            const btn = modal.querySelector(".ant-btn-primary");
            if (btn && btn.textContent.trim() === "确定") btn.click();
            break;
        }
    }
}''')
```

### 商品编码

产品SKU唯一编码字段。有两种方式：
1. **一键生成：** 输入框旁有「一键生成  · 高级」按钮，点击自动生成编码
2. **手动输入：** 直接在输入框填自定义编码

**注意：** 商品编码每行SKU独立，批量模式不适用。如有多个SKU，各SKU行需分别处理。

## SKU 定价栏完整操作流程

```python
async def fill_sku_pricing_section(page):
    """完整处理SKU定价栏"""
    # 1. 切到产品信息tab
    await page.evaluate("""() => {
        const items = document.querySelectorAll('.anchor-menu-item');
        for (let item of items) {
            if (item.textContent.trim() === '产品信息') {
                item.click(); break;
            }
        }
    }""")
    await asyncio.sleep(2)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.8)")
    await asyncio.sleep(1)
    
    # 2. 批量填零售价/货值/库存/重量
    inputs = await page.locator('table').nth(11) \
        .locator('tr').first.locator('input').all()
    for i, val in enumerate(['1.30', '1.30', '2000', '0.2']):
        await inputs[i].fill(val)
    await page.get_by_text('批量填充').first.click()
    
    # 3. 填包装尺寸（如有）
    # 每个SKU行的长/宽/高三输入框
    
    # 4. 是否原箱 → 是
    selects = await page.locator('table').nth(11).locator('select').all()
    for sel in selects:
        opts = [await o.get_attribute('value') for o in await sel.locator('option').all()]
        if '' in opts and '0' in opts and '1' in opts:
            await sel.select_option('1')
    
    # 5. 物流属性（按用户指示）
    # 6. 商品编码 - 点一键生成
    
    await asyncio.sleep(1)
    print("SKU定价栏填充完成")
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*