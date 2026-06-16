# 店小秘图片编辑工作流

> 通过 CDP/Playwright 操作用户 Chrome 浏览器，在店小秘 SPA 中编辑产品图片。

## 目录
1. [图片尺寸调整（批量改图）](#图片尺寸调整)
2. [PC端描述图片尺寸调整](#pc端描述图片尺寸调整)
3. [营销图一键生成](#营销图一键生成)
4. [Ant Design 弹窗交互要点](#ant-design-弹窗交互要点)

---

## PC端描述图片尺寸调整

> **⚠️ 与产品图片区的批量改图操作步骤不同！** 不可混用。

### 触发路径
```
描述信息 → PC端描述 → 展开图片栏 → 批量编辑图片 → 批量改图片尺寸 → 弹窗
```

### 操作步骤（已验证 2026-06-12）

| 步骤 | 操作 | 说明 |
|:--:|:--|:--|
| 1 | 点击「描述信息」tab | 切换至描述信息编辑区 |
| 2 | 点击CKEditor工具栏「展开图片栏」 | 展开图片操作工具栏 |
| 3 | 点击「批量编辑图片」下拉 | 打开操作菜单 |
| 4 | 选择「批量改图片尺寸」 | 打开批量改图弹窗 |
| 5 | 第一个下拉选「自定义比例调整」 | 从「等比例调整」改为「自定义比例调整」 |
| 6 | 第二个下拉「图片小边」**不动** | ✅ 保持默认，不要更改 |
| 7 | 输入框**变化至**填 **800** | 图片小边调整为800px |
| 8 | 点击「生成JPG图片」 | 执行批量调整 |

### 关键区别（ vs 产品图片区）

| 项目 | 产品图片区 | PC端描述区 |
|:--|:--|:--|
| 触发路径 | 编辑图片 → 批量改图片尺寸 | 展开图片栏 → 批量编辑图片 → 批量改图片尺寸 |
| 第一个下拉 | 等比例调整 → **自定义比例调整** | 等比例调整 → **自定义比例调整** |
| 第二个下拉 | 图片宽 → **自定义宽高** | **图片小边（不动）** |
| 输入 | 宽800 + 高800 | 变化至 800 |
| 结果 | 精确800×800 | 图片小边变为800px，另一边等比缩放 |

---

## ⚠️ 重要：两个不同的批量改图入口（2026-06-12 用户纠正）

**这两个入口操作步骤完全不同，严禁混用。**

| 入口 | 位置 | 触发方式 |
|:--|:--|:--|
| 产品主图 | 产品信息 → 产品图片 → 编辑图片 → 批量改图片尺寸 | `编辑图片`下拉 → `批量改图片尺寸` |
| 描述图片 | 描述信息 → PC端描述 → 批量编辑图片 → 批量改图片尺寸 | CKEditor `展开图片栏` → `批量编辑图片`下拉 → `批量改图片尺寸` |

**规则：** 用户说「批量编辑图片」时，先确认是哪个入口。产品图片的操作步骤不能用在描述图片上。PC端描述批量改尺寸**不需要**改第二个下拉（图片小边保持不动），只需改第一个下拉为自定义比例调整 + 填变化至800。

## 图片尺寸调整（PC端描述图片入口）

### 触发路径
```
描述信息 tab → 点击CKEditor工具栏「展开图片栏」→ 点击展开的「批量编辑图片」下拉 → 「批量改图片尺寸」→ 弹窗
```

### 操作步骤（与产品图片完全不同）

| 步骤 | 操作 | 说明 |
|:--|:--|:--|
| 1 | 点击「展开图片栏」 | CKEditor工具栏上的按钮（title="展开图片栏"） |
| 2 | 点击「批量编辑图片」 | 展开的图片栏中的下拉按钮（a.img-options-action-btn.ant-dropdown-trigger） |
| 3 | 点击「批量改图片尺寸」 | 下拉菜单项 |
| 4 | 第一个下拉：等比例调整 → **自定义比例调整** | 鼠标坐标点击打开（page.mouse.click） |
| 5 | 第二个下拉：**图片小边（不要动！）** | ❌ 产品图片要改第二个下拉，但描述图片这里**不动** |
| 6 | 输入框：变化至 → 填 **800** | 用 nativeInputValueSetter |
| 7 | 点击「生成JPG图片」 | 弹窗关闭 |

### ⚠️ 关键区别（与产品图片入口对比）

| 维度 | 产品图片 | PC端描述图片 |
|:--|:--|:--|
| 触发入口 | `编辑图片` → `批量改图片尺寸` | `展开图片栏` → `批量编辑图片` → `批量改图片尺寸` |
| 第一个下拉 | 等比例调整 → **自定义比例调整** | 等比例调整 → **自定义比例调整**（相同） |
| 第二个下拉 | 图片宽 → **自定义宽高** | **图片小边（不要动！）** |
| 输入 | 宽:800, 高:800（两个输入框） | 变化至:800（一个输入框） |

## 图片尺寸调整（产品图片入口）

### 触发路径
```
产品图片区 → 点击「编辑图片」→ 下拉菜单「批量改图片尺寸」→ 弹窗
```

### 步骤详解

#### 1. 打开编辑图片下拉菜单
编辑图片按钮的 HTML 结构：
```html
<a class="img-options-action-btn ant-dropdown-trigger">
  <div class="ant-flex ...">
    <span class="attach-icons md-18">crop</span>
    <span class="m-left5 m-right5">编辑图片</span>
    <i class="iconfont icon_down"></i>
  </div>
</a>
```

点击方式：
```python
# 方式A：Playwright 原生 click
page.locator('a.img-options-action-btn.ant-dropdown-trigger').first.click()

# 方式B：若原生 click 被弹窗遮挡，用 evaluate dispatchEvent
page.evaluate("""
    () => {
        const btn = document.querySelector('a.img-options-action-btn.ant-dropdown-trigger');
        if (btn) {
            btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
            return 'clicked';
        }
    }
""")
```

#### 2. 点击「批量改图片尺寸」
下拉菜单项可能不可见（`display: none` 或被页面其他元素遮挡）。用 evaluate dispatchEvent 强制触发：
```python
page.evaluate("""
    () => {
        const items = document.querySelectorAll('.ant-dropdown-menu-item');
        for (const item of items) {
            if (item.textContent.trim().includes('批量改图片尺寸')) {
                item.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
                return 'clicked';
            }
        }
    }
""")
```

#### 3. 选中目标图片（取消全选→单选）
弹窗中有一个图片网格（`class="grid-row"`），每个图片项是 DIV，显示文字如 `点击选中 800 X 800` 或 `点击取消 790 X 1007`。

- `点击取消` = 当前选中（点击可取消选择）
- `点击选中` = 当前未选（点击可选中）

```python
# Step 3a: 点击「选择全部」切换全选状态
page.evaluate("""
    () => {
        const els = document.querySelectorAll('*');
        for (const el of els) {
            if (el.textContent.trim() === '选择全部' && el.children.length === 0) {
                el.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));
                return;
            }
        }
    }
""")
time.sleep(1)

# Step 3b: 只选目标图片（例如 790x1007 那张）
page.mouse.click(x_center, y_center)  # 从 grid-row 的子 DIV 坐标计算
```

#### 4. 设置「自定义比例调整」+「自定义宽高」（关键步骤）

> ⚠️ **必须同时改两个下拉**：第一个从「等比例调整」→「自定义比例调整」，第二个从「图片宽」→「自定义宽高」。只改第一个不改第二个，高度会按比例自动算（如800×1020），不是精确的800×800。

点击第一个下拉选择器切换到自定义比例调整模式：
```python
# 点击第一个 search 输入（等比例调整选择器）
page.evaluate("""
    () => {
        const wraps = document.querySelectorAll('.ant-modal-wrap');
        for (const w of wraps) {
            if (w.style.display !== 'none') {
                const inputs = w.querySelectorAll('input[type="search"]');
                if (inputs.length > 0) inputs[0].click();
            }
        }
    }
""")
time.sleep(2)

# 选择「自定义比例调整」选项
page.evaluate("""
    () => {
        const dds = document.querySelectorAll('.ant-select-dropdown');
        for (const dd of dds) {
            if (dd.style.display !== 'none') {
                const items = dd.querySelectorAll('.ant-select-item-option');
                for (const item of items) {
                    if (item.textContent.includes('自定义比例调整')) {
                        item.click(); return;
                    }
                }
            }
        }
    }
""")
```

#### 5. 设置第二个下拉：从「图片宽」→「自定义宽高」

设置完第一个下拉后，点击第二个 search 输入框（原为「图片宽」），选择「自定义宽高」：

> ⚠️ **CDP 模式坑：** 在 `connect_over_cdp` 模式下，`inputs[1].click()`（JS 原生 click）**打不开**第二个下拉选择器（Ant Design Select 的搜索输入框）。必须用 `page.mouse.click(x, y)` 模拟真实鼠标点击。坐标通过 `getBoundingClientRect()` 获取。

```python
# 获取第二个 search 输入的坐标，用 mouse.click 点击
pos = page.evaluate("""
    () => {
        const wraps = document.querySelectorAll('.ant-modal-wrap');
        for (const w of wraps) {
            if (w.style.display !== 'none') {
                const inputs = w.querySelectorAll('input[type="search"]');
                if (inputs.length >= 2) {
                    const r = inputs[1].getBoundingClientRect();
                    return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
                }
            }
        }
        return null;
    }
""")
if pos:
    page.mouse.click(pos['x'], pos['y'])
time.sleep(2)

# 检查下拉选项是否弹出
options = page.evaluate("""
    () => {
        const result = [];
        const all = document.querySelectorAll('.ant-select-item-option');
        for (const el of all) {
            if (el.offsetParent !== null) result.push(el.textContent.trim());
        }
        return result;
    }
""")
# 期待看到 ['图片宽', '图片高', '自定义宽高']

# 选择「自定义宽高」
page.evaluate("""
    () => {
        const items = document.querySelectorAll('.ant-select-item-option');
        for (const item of items) {
            if (item.offsetParent !== null && item.textContent.includes('自定义宽高')) {
                item.click(); return;
            }
        }
    }
""")
time.sleep(1)
```

> 成功标志：弹窗中原先只有一个 text 输入框（宽），选中「自定义宽高」后出现第二个 text 输入框（高）。当前选择器状态可通过查询 `.ant-select-selection-item` 验证，预期值 `['自定义比例调整', '自定义宽高']`。

#### 6. 设置宽度和高度并生成
```python
# 设置宽度 800
page.evaluate("""
    () => {
        const wraps = document.querySelectorAll('.ant-modal-wrap');
        for (const w of wraps) {
            if (w.style.display !== 'none') {
                const inputs = w.querySelectorAll('input');
                for (const inp of inputs) {
                    if (inp.type === 'text') {
                        const setter = Object.getOwnPropertyDescriptor(
                            HTMLInputElement.prototype, 'value'
                        ).set;
                        setter.call(inp, '800');
                        inp.dispatchEvent(new Event('input', {bubbles: true}));
                        inp.dispatchEvent(new Event('change', {bubbles: true}));
                        return;
                    }
                }
            }
        }
    }
""")

# 点击「生成JPG图片」按钮
page.mouse.click(x, y)  # 按钮位置: (809, 148) 左右
```

### ✅ 已验证标准步骤（2026-06-12 用户指定并验证）

**这是当前唯一的正确做法。** 之前的尝试失败是因为只改了第一个下拉（自定义比例调整），没改第二个下拉（图片宽→自定义宽高）。

操作序列：

1. **点击「编辑图片」** → 下拉中选择「批量改图片尺寸」
2. **第一个下拉**：「等比例调整」→ **「自定义比例调整」**
3. **第二个下拉**：「图片宽」→ **「自定义宽高」**
   - ⚠️ CDP 模式下第二个下拉必须用 `page.mouse.click(x, y)` 坐标点击打开（JS click 不生效）
   - 获取坐标：`inputs[1].getBoundingClientRect()` → x+r.w/2, y+r.h/2
   - 打开后下拉选项为：`['图片宽', '图片高', '自定义宽高']`
4. **两个输入框**分别填 **800**（宽）和 **800**（高）
5. 点击 **「生成JPG图片」**
6. 验证：6 张主图全部变为 800×800

> ✅ **此路径已验证可以正确处理 1600×1600 图片。** 之前失败的原因是只改了第一个下拉，第二个下拉仍是「图片宽」导致高度被等比计算（如800×1020）而不是精确800×800。

### 用户交互风格注记（2026-06-12 用户强调）

此操作序列中，用户要求**每步做完汇报，等下一步指令**。严禁一次做完所有步骤然后说"搞定"。正确的做法是：
1. 用户说第1步 → 做完 → 汇报 → 等用户说第2步
2. 用户说第2步 → 做完 → 汇报 → 等用户说第3步
3. ...以此类推

详见 SKILL.md 中「严格按用户指令操作——步进模式」章节。

### 弹窗工具栏布局（y坐标约148-155）
```
y=148 [等比例调整选择器] [图片宽选择器] [px]    [生成JPG图片] [生成PNG图片]  [记住本次设置☐]
y=200 [选择全部☐]
```

---

## 营销图一键生成

位置：产品图片区下方，「营销图片」分区。

```python
# 滚动到营销图片区域
page.evaluate("""
    () => {
        const spans = document.querySelectorAll('span');
        for (const sp of spans) {
            if (sp.textContent.includes('营销图片')) {
                sp.scrollIntoView({block: 'start'});
                return;
            }
        }
    }
""")

# 点击「一键生成」按钮（有两个选项：白底图和场景图）
gen_btn = page.locator('button, span').filter(has_text='一键生成').first
gen_btn.click()
# 店小秘自动生成白底图 + 场景图
```

---

## Ant Design 弹窗交互要点

### 下拉菜单位置偏移问题
Ant Design 的 dropdown portal 有时渲染到 y 坐标为负值的位置（页面滚动后计算错误）。
**症状**：dropdown DOM 存在但 `display: none` 或在视口外。
**解决**：用 `page.evaluate` 在 DOM 中找到目标元素并直接 `dispatchEvent('click')`，不依赖可见性。

### 弹窗被其他弹窗遮挡
店小秘可能有残留弹窗（如物流属性模态框）未关闭，导致新弹窗无法触发。
**解决**：操作前多次按 Escape 关闭所有弹窗：
```python
for _ in range(3):
    page.keyboard.press('Escape')
    time.sleep(0.3)
```

### 图片网络结构（Resize Modal）
```
.ant-modal-wrap (可见的)
  └── .ant-modal-content
       ├── .ant-modal-header → "批量改图片尺寸"
       ├── .ant-modal-body
       │    ├── toolbar 行 (selectors + buttons + checkboxes)
       │    └── .grid-row (图片网格)
       │         ├── DIV [0] → "点击取消 800 X 800"  (thumb 115x115)
       │         ├── DIV [1] → "点击取消 800 X 800"
       │         ├── DIV [2] → "点击取消 800 X 800"
       │         ├── DIV [3] → "点击取消 790 X 1007" ← 目标
       │         ├── DIV [4] → "点击取消 800 X 800"
       │         └── ... (每行8列)
       └── .ant-modal-footer
```
图片项是 `grid-row > DIV`，每个 DIV 代表一张图，文字包含尺寸和选择状态。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*