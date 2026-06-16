# 店小秘 SKU 变种配置

> 在产品信息 tab 中配置颜色/SKU/价格/库存。

## 颜色变种规律

- 新商品导入时，颜色属性选项中有很多「该属性值平台已废弃，不支持选择！」的选项
- 用户已上架商品使用 白/黑/军绿色（迷你风扇）或 白/黑/银（空气净化器）
- 先选择有效颜色，然后填入「自定义名称」（英文，如 White/Black/Silver）

### ⚠️ 重要：颜色标签不重要，自定义名称才重要

**用户明确说：**「它这个颜色里面你不用管。因为给前台展示的只会展示自定义名称，只要我们自定义名称是正确的就可以」

实操含义：
- 如果AliExpress属性列表里没有「银色」——选最接近的（浅灰色、灰色等），**不要纠结**
- 不用花时间找完美匹配的系统颜色标签
- 自定义名称写对就行（White / Black / Silver）
- 买家看到的是自定义名称，不是系统颜色标签

## SKU 表（VXE Table）字段

店小秘的SKU表格使用 **VXE Table**（Vue.js虚拟表格组件），输入框通过 `placeholder` 属性定位。Table结构如下：

### 字段顺序（每行从左到右）

| 序号 | placeholder | 说明 | 设置值 |
|:--:|:--|:--|:--:|
| 0 | （自定义名称输入框） | 英文颜色名 | White / Black / Silver |
| 1 | (select) | 颜色 | 从AliExpress属性列表选 |
| 2 | 零售价 | React受控组件 | 公式计算值 |
| 3 | 货值 | 可留空（自动计算？） | — |
| 4 | 库存 | 1688导入的可能有旧产品ID | 1000 |
| 5 | 重量 | kg | 0.080 |
| 6 | 长 | cm | 6 |
| 7 | 宽 | cm | 3 |
| 8 | 高 | cm | 2 |
| 9 | (select) | 是否原箱/物流属性 | 按需 |
| 10 | EAN code | 可选 | 留空 |
| 11 | 商品编码 | 可选 | 一键生成或留空 |

### ⚠️ VXE Table 尺寸/重量字段：nativeInputValueSetter 对校验无效（2026-06-09）

VXE Table 的输入框（长/宽/高/重量）通过 nativeInputValueSetter 设置值后，虽然 DOM 值显示正确（如 `6`），但 **React 表单校验仍报「请填写整数」错误**。这是因为 VXE 的校验依赖于真实的键盘事件序列，而非属性修改。

**修复方法——必须用键盘模拟输入：**

```python
# 1. 先在页面上找到出错的输入框（在 .ant-form-item-has-error 内）
page.evaluate('() => {
    const items = document.querySelectorAll(".ant-form-item-has-error");
    for (const item of items) {
        if ((item.textContent || "").includes("包装后尺寸")) {
            const inputs = item.querySelectorAll("input");
            if (inputs.length > 0) { inputs[0].focus(); inputs[0].click(); return; }
        }
    }
}')
time.sleep(0.5)

# 2. 键盘模拟：全选 → 删除 → 输入 → Tab 到下一个
page.keyboard.press('Control+a')    # 全选
time.sleep(0.2)
page.keyboard.press('Delete')        # 删除
time.sleep(0.2)
page.keyboard.type('6')              # 输入新值
time.sleep(0.2)
page.keyboard.press('Tab')           # 跳到宽输入框
time.sleep(0.3)
page.keyboard.type('6')
time.sleep(0.2)
page.keyboard.press('Tab')           # 跳到高输入框  
time.sleep(0.3)
page.keyboard.type('6')
time.sleep(0.2)
page.keyboard.press('Tab')
time.sleep(0.5)

# 3. 验证错误已清除
errors = page.evaluate("() => document.querySelectorAll('.ant-form-item-explain-error').length")
```

**注意：** 此修复必须在**包装信息 tab** 下操作，且操作前确保输入框可见（先 scrollIntoView）。

### 表格结构

表格有4组输入（index 0-3）：
- **index 0**: 全局基础行（库存空，重量/尺寸填原始数据）
- **index 1-3**: 各颜色SKU行（每行对应一个颜色）

### 1688导入的库存值陷阱

1688导入的商品，库存字段可能被填为**1688产品ID**而非实际库存数。**必须检查并覆写！**

典型值（来自本次实操）：
- 白色: 78656、78708、78656（实为1688产品号）
- 黑色: 52272、52372
- 银色: 79285、79440

### 库存规则（用户强制标准）

**所有新品必须套用此规则，不得随意写库存数字：**

1. 打开1688产品页面，找到各颜色的「库存N件」数值
2. 若1688库存 > 2000 → 写 **2000**（封顶）
3. 若1688库存 ≤ 2000 → 如实写1688的数字

**验证方法：** 在1688产品页文本中搜索「库存」关键字，一般格式为「颜色 → 库存N件」例：
```
银色 → 库存79440件
白色 → 库存78708件
黑色 → 库存52372件
```
注意：1688可能有多个产品页（同款不同价），需确认用的是哪一个产品的库存数据。


## 零售价 React 设置技巧

零售价字段使用受控 React 组件（用 `v-model` 或 `onChange` 驱动），直接 `input.value = '69.00'` 无效。**注意有4个零售价输入框**（1个全局 + 3个SKU行），需要全部设置：

```python
# 正确的做法 — 全部4个零售价输入框
page.evaluate("""
    () => {
        const inputs = document.querySelectorAll('input[placeholder="零售价"]');
        const setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        inputs.forEach(inp => {
            setter.call(inp, '51.99');
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
            inp.dispatchEvent(new Event('blur', { bubbles: true }));
        });
        return inputs.length;  // 应该返回4
    }
""")
```

如果一次不行，尝试 `focus()` + `select()` + `value=''` 后再设值。

## VXE Table 单元格发现技巧

店小秘SKU表格使用 VXE Table（虚拟表格），其单元格可能是纯文本 `<td>` 而非 `<input>`。来源URL采集导入的数据（如价格 20.88）存在于 `<td>` 文本中，同时每行也有对应的 `<input placeholder="零售价">` 输入框。

**发现隐藏输入框的方法：**

当页面显示的值（如"20.88"）是纯文本 `<td>` 而非输入框时，先用 `document.createTreeWalker` 找到文本节点，再沿DOM树向上定位到包含输入框的行：

```python
# 步骤1：找到所有包含特定值的文本节点及其父元素
data = page.evaluate("""() => {
    const walker = document.createTreeWalker(
        document.body,
        4,  // NodeFilter.SHOW_TEXT
        null, false
    );
    const results = [];
    let node;
    while (node = walker.nextNode()) {
        if (node.textContent.includes('20.88')) {
            const parent = node.parentElement;
            results.push({
                text: node.textContent.trim(),
                parentTag: parent.tagName,
                parentHTML: parent.outerHTML.substring(0, 400),
                grandparentHTML: parent.parentElement?.outerHTML?.substring(0, 600) || ''
            });
        }
    }
    return JSON.stringify(results, null, 2);
}""")

# 从grandparentHTML中可以看到行结构，
# 从而发现实际上每行有 input[placeholder="零售价"] 输入框

# 步骤2：按placeholder定位所有输入框
inputs = page.evaluate("""() => {
    const inputs = document.querySelectorAll('input[placeholder="零售价"]');
    const setter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype, 'value'
    ).set;
    inputs.forEach(inp => {
        setter.call(inp, '51.99');
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
    });
}""")
```

此技巧通用——当页面显示的值你找不到输入框时，用 treeWalker 找文本节点后沿DOM树向上追溯即可发现真正的表单元素。


## 商品编码一键生成

### 已验证产品编码（挂脖空气净化器 ID:[PHONE_REDACTED]5663520）

| SKU | 颜色 | 自定义名称 | 商品编码 | 生成方式 |
|:--:|:--|:--:|:--:|:--|
| 1 | 白色 | White | **White** | 一键生成→设置（无前缀） |
| 2 | 黄色 | Black | **Black** | 一键生成→设置（无前缀） |
| 3 | 红色 | Silver | **Silver** | 一键生成→设置（无前缀） |

**规律：** 无编码前缀时，系统自动用自定义颜色英文名作为商品编码。

### 前置检查：物流属性必须已设

**必须先设物流属性，再生成商品编码。** 如果物流属性是空的，点击一键生成后会报「物流属性必填！」错误，且无法生成编码。

### 编码前缀决定逻辑（用户规范）

弹窗结构：标题「商品编码」，输入框 `name="skuPrefix" placeholder="编码前缀"`，按钮「设置」(`.ant-btn-primary`)。

1. **打开1688产品页**，搜索 **货号** / **型号** / **产品编号** 关键词
2. **如果有货号**（如 CE.0131）→ 输入为编码前缀
3. **如果没有货号** → 留空前缀，直接点「设置」，系统自动用自定义颜色名（White/Black/Silver）作为编码

```python
# 步骤1：点击一键生成（是 span.link，不是 button！）
# 注意：必须在商品编码表头列的正下方找，不是营销图的
page.evaluate("""
    () => {
        const spans = document.querySelectorAll('span.link');
        for (const span of spans) {
            if (span.textContent?.trim() === '一键生成') {
                span.click();
                return;
            }
        }
    }
""")
time.sleep(1.5)

# 步骤2：模态弹窗出现，有 input[placeholder="编码前缀"] + button:设置
# 如果1688无货号 - 留空前缀，直接点设置
# 如果有货号 - 先填前缀再点设置
page.evaluate("""
    () => {
        const wraps = document.querySelectorAll('.ant-modal-wrap');
        for (const w of wraps) {
            if (w.offsetWidth > 0 && w.offsetHeight > 0) {
                const btns = w.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent?.trim() === '设置') {
                        btn.click();
                        return;
                    }
                }
            }
        }
    }
""")
```

### 验证

生成后检查 `input[placeholder="商品编码"]` 的值。无前缀时自动用自定义颜色名：
- White / Black / Silver

注意：页面中有多个「一键生成」文本（营销图、商品编码），需通过前一个步骤确定点击的是正确的。营销图的一键生成在「产品信息」tab，商品编码的一键生成在SKU表格的表头列。

### 是否原箱 — 纯HTML Select设置

「是否原箱」字段使用原生 `<select>` 元素（非Ant Design），可以直接用 `selectedIndex` 设置：

### ⚠️ 重要：共5个select，要设4个！ 用户曾纠正我漏了最后一个。

```python
page.evaluate("""
    () => {
        const selects = document.querySelectorAll('select');
        // 索引结构（共5个）：
        //   0: 颜色筛选下拉（全部颜色/白色/黄色/红色...）→ **不要动！**
        //   1: 全局行是否原箱
        //   2: White SKU行是否原箱
        //   3: Black SKU行是否原箱
        //   4: Silver SKU行是否原箱
        // 选项：请选择(0) / 否(1) / 是(2)
        // 必须设索引1,2,3,4（共4个），漏了任何一个用户都会发现！
        for (let idx = 1; idx <= 4; idx++) {
            selects[idx].selectedIndex = 2;  // 选"是"
            selects[idx].dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
""")
```

验证方法：`page.evaluate("() => Array.from(document.querySelectorAll('select')).slice(1,5).map(s => s.options[s.selectedIndex]?.text)")` 应返回 `['是', '是', '是', '是']`

## 物流属性（批量编辑Modal）

物流属性使用 **Ant Design Modal + 自定义checkbox树形组件**。点击表头 `物流属性` 列下的 `(批量)` 链接打开。

### Modal结构

Modal打开后显示为树形结构，每行格式：`类别: [checkbox] 选项名`

```
物流属性
禁运: □禁运
普货: □普货
纯电: □纯电
强磁: □强磁
特货: □液体 □粉末 □膏体 □特货其他
特敏: □危险品 □特敏其他
内电: □干电池 □铅酸蓄电池 □镍氢电池 □其他电池
     □纽扣式锂电池 □非纽扣锂金属电池 □充电盒式蓝牙耳机
     □非纽扣锂离子电池  ← 挂脖空气净化器等USB充电内置锂电产品选此项
外电: □外电
弱磁: □弱磁
[取消] [确定]
```

### 电池类型选择指南

| 产品类型 | 选择 |
|:--|:--|
| USB充电、内置不可拆卸锂电池（挂脖风扇/空气净化器） | 内电 → **非纽扣锂离子电池** |
| 纽扣电池（手表/计算器） | 内电 → **纽扣式锂电池** |
| 干电池供电（手电筒） | 内电 → **干电池** |
| 纯电池类产品（充电宝/18650） | 纯电 |
| 不带电产品 | 普货 |

### 操作代码

```python
# 步骤1：点击物流属性表头的(批量) span.link
page.evaluate("""
    () => {
        const ths = document.querySelectorAll('th');
        for (const th of ths) {
            if (th.innerText.includes('物流属性')) {
                const spans = th.querySelectorAll('span.link');
                for (const span of spans) {
                    if (span.textContent?.trim() === '批量') {
                        span.click();
                        return;
                    }
                }
            }
        }
    }
""")
time.sleep(1.5)

# 步骤2：在弹窗中点击目标电池类型（checkbox）
page.evaluate("""
    () => {
        const wraps = document.querySelectorAll('.ant-modal-wrap');
        for (const w of wraps) {
            if (w.offsetWidth > 0 && w.offsetHeight > 0) {
                const allItems = w.querySelectorAll('*');
                for (const item of allItems) {
                    const t = item.textContent?.trim() || '';
                    if (t === '非纽扣锂离子电池') {
                        item.click();
                        return;
                    }
                }
            }
        }
    }
""")
time.sleep(1)

# 步骤3：点击确定
page.evaluate("""
    () => {
        const wraps = document.querySelectorAll('.ant-modal-wrap');
        for (const w of wraps) {
            if (w.offsetWidth > 0 && w.offsetHeight > 0) {
                const btns = w.querySelectorAll('button');
                for (const btn of btns) {
                    if (btn.textContent?.trim() === '确定') {
                        btn.click();
                        return;
                    }
                }
            }
        }
    }
""")
```

### 常见问题

- 批量弹窗可能同时存在多个（来自不同操作），注意确认打开的是物流属性Modal（标题栏显示「物流属性」）
- 电池类型选择是checkbox，可以多选（如果一个产品有多个电池类型）
- 如果选完后关闭Modal再打开，之前的选中状态会保留
- （批量）是一键应用给所有SKU行的，不需要逐行设置
- 物流属性**务必先设**再生成商品编码，否则报「物流属性必填！」

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*