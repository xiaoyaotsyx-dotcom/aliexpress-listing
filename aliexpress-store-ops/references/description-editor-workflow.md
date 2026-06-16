# 店小秘 描述信息编辑工作流

> PC端描述 + 无线端描述 的完整操作流程。覆盖 CKEditor 工具栏操作、批量改图片尺寸、引用模板、新版编辑器切换、一键生成等所有实操细节。

## 一、PC端描述

PC端描述使用 CKEditor（店小秘定制版），工具栏包含：
- 选择图片 / 批量编辑图片 / 引用模板 / AI生成
- 源码 / 全屏 / 样式 / 字体 / 大小 / 段落

### 1.1 引用模板（关联营销模块）

**操作步骤：**
1. 点击工具栏的 **「引用模板」** 按钮（CSS class: `cke_button__smttemplateprops`）
2. 弹出「选择产品信息模块」对话框，包含 tab：关联营销(速卖通) / 自定义模板 / 尺码模板
3. 默认在「关联营销(速卖通)」tab，列表显示已有模块
4. 找到目标模块行（如 **mini fan**），该行包含4列：模块名称 / 模块类型 / 最后更新时间 / **操作**
5. 操作列有一个 **Ant Design checkbox**（class: `ant-checkbox-input`），点击选中
6. 点击底部 **「选择」** 按钮关闭对话框
7. 模板内容（含关联产品 widget + 图片）自动加载到 CKEditor 中

**坑点：**
- 对话框是 Ant Design Modal，checkbox 在最后一列 `<td>` 中（class: `ant-checkbox-wrapper`）
- 选中后必须点「选择」而非「关闭」，否则不生效
- 已选中的模块会在编辑器中显示为 `offer-template-0` div，含 20+ 张图片
- ⚠️ **堆叠弹窗**：每次点「引用模板」都会开一个新弹窗，不会自动关闭之前的。连续点击会产生 3+ 层重叠弹窗。修复：先通过 `.ant-modal-close` 关闭所有可见弹窗，再重新点「引用模板」
- 验证模板是否加载成功：检查 CKEditor iframe body.innerHTML 是否包含 `offer-template-0`

### 1.2 批量改图片尺寸

**操作步骤：**
1. 点击 CKEditor 工具栏的 **「批量编辑图片」** combo（class: `cke_combo__batcheditimgdropdow`）
2. 弹出 CKEditor 面板（以 **iframe** 方式渲染，class: `cke_panel_frame`）
3. 在面板中找到 **「批量改图片尺寸」** 选项（一个 `<a>` 链接），点击
4. 弹出 Ant Design Modal「批量改图片尺寸」
5. 在模态框中：
   a. 第一个 Ant Select「等比例调整」→ 改为 **「自定义比例调整」**
   b. 第二个 Ant Select「图片小边」→ 改为 **「图片宽」**
   c. 输入框填 **800**（nativeInputValueSetter + dispatchEvent）
   d. 点击 **「选择全部」**（选中所有图片）
   e. 点击 **「生成JPG图片」**
6. 模态框自动关闭，图片全部变为 800px 宽（高度按比例缩放）

**关键技巧：**
- CKEditor 面板内容在 **iframe** 中，需要通过 `frame.contentDocument || frame.contentWindow.document` 访问
- Ant Design Select 下拉在 modal 中用 `mouse.click` 触发（JS evaluate `.click()` 有时不触发 dropdown）
- 下拉选项（`.ant-select-item-option`）通过 portal 渲染到 DOM 中，用 `.ant-select-item-option` 选择器搜索
- 必须先选图片（选择全部）再点生成，否则报「错误：请选择要更改尺寸的图片」

**验证：**
- 模态框关闭 = 成功
- CKEditor iframe 中图片的 `width` 属性变为 800
- 编辑器字符数可能增加（JPG 重压缩后图片替换）

---

## 二、无线端描述

### 2.1 使用新版编辑器（2026-06-08 验证通过）

店小秘的无线端描述有3种模式（Ant Design radio group）：
- **不填写无线端描述**（radio）
- **使用老版编辑器**（radio）
- **使用新版编辑器**（radio，用户操作目标）

**关键操作规则（Ant Design radio buttons）：**
⚠️ 必须点击 `<label class="ant-radio-wrapper">` 元素，不能点击内部的 `<span>`。
Ant Design 的 radio 通过 label 的 click 事件处理状态切换，span 的 click 不会触发。

### 2.2 完整操作流程（2026-06-08 Hermes browser tool CDP 验证通过）

**前置条件：** 使用 Hermes 内置 browser 工具（已配置 `browser.cdp_url` 连用户 Windows Chrome）

**步骤1：切换到新版编辑器**
```
点击「使用新版编辑器」的 label 元素（class: ant-radio-wrapper）→ radio 选中
```
确认方法：`label.querySelector('.ant-radio').classList.contains('ant-radio-checked')` 返回 true

**步骤2：在新版编辑器弹窗中点「根据PC端描述一键生成」**
```
新版编辑器以 Ant Design Modal 形式弹出（class: ant-modal smt-new-editor）
在弹出的 modal 中找到 → title-right 区域 → span.link「根据PC端描述一键生成」→ 点击
```
这个按钮在 modal 内部的 `.title-right` 区域，是一个 `<span class="link">` 元素。

**步骤3：确认替换**
```
弹窗提示：「一键生成会替换掉现有无线端内容，确定一键生成吗？」
→ 点击「确定」按钮
```

**步骤4：验证生成结果**
生成的无线端内容以模块形式展示在编辑器窗口中：
- 文字（模块数/30）
- 图片（模块数/30）✅ 通常生成1个图片模块
- 图文（模块数/15）
- 视频（模块数/1）

### 2.3 无线端 CKEditor 旧版编辑器（备用方案）

如果用户选择使用老版编辑器（而非新版编辑器弹窗），CKEditor 实例映射：

| 实例名 | 用途 | PC/Wireless |
|:--|:--|:--|
| `ckeditor30` | PC端描述 | PC |
| `ckeditor29` | 无线端描述 | Wireless |

通过 `CKEDITOR.instances` 访问，也可通过 DOM 查询：
```javascript
document.querySelector('#cke_ckeditor30 .cke_wysiwyg_frame')  // PC
document.querySelector('#cke_ckeditor29 .cke_wysiwyg_frame')  // 无线
```

**旧版编辑器下复制PC内容到无线端（CKEditor API fallback）：**
```javascript
// 获取PC端内容
var pcData = CKEDITOR.instances['ckeditor30'].getData();
// 设置到无线端
CKEDITOR.instances['ckeditor29'].setData(pcData);
// 点击橙色保存按钮
```
仅在用户明确指示使用老版编辑器时使用此方法。

---

## 三、CKEditor 面板操作（通用）

CKEditor 的 combo/dropdown 使用 iframe 渲染，操作方式与普通 Ant Design 组件不同：

### 识别 CKEditor 面板

```python
# 点击 CKEditor combo
pg.mouse.click(combo_x, combo_y)
time.sleep(2)

# 查找面板 iframe
panel_frame = pg.evaluate("""
    () => {
        const frames = document.querySelectorAll('.cke_panel_frame');
        for (const f of frames) {
            const r = f.getBoundingClientRect();
            if (r.width > 0 && r.y > 0) return {x: r.x, y: r.y, w: r.width, h: r.height};
        }
        return null;
    }
""")
```

### 操作面板选项

**方式一（推荐·2026-06-11 验证通过）：Playwright `frame_locator`**

```python
# 1. 先点击 combo 按钮打开面板
page.evaluate("""() => {
    var combo = document.querySelector('.cke_combo__batcheditimgdropdow .cke_combo_button');
    if (combo) combo.click();
}""")
time.sleep(3)

# 2. 用 frame_locator 访问 iframe 内容
panel_frame = page.frame_locator('iframe.cke_panel_frame')
links = panel_frame.locator('a')
count = links.count()
for i in range(count):
    text = links.nth(i).inner_text()
    if '批量改图片尺寸' in text:
        links.nth(i).click()
        break
```

**方式二：通过 JS contentDocument 访问（备用）**

```python
result = pg.evaluate("""
    () => {
        const frame = document.querySelector('.cke_panel_frame');
        try {
            const doc = frame.contentDocument || frame.contentWindow.document;
            const links = doc.querySelectorAll('a');
            for (const link of links) {
                if (link.textContent?.trim() === '目标选项文字') {
                    link.click();
                    return 'CLICKED';
                }
            }
            return Array.from(links).map(l => l.textContent?.trim());
        } catch(e) {
            return 'ERROR: ' + e.message;
        }
    }
""")
```

**坑点：**
- CDP 模式下 CKEditor combo panel 以 `iframe.cke_panel_frame` 渲染，不在主 DOM 中
- 面板打开后需要 2-3 秒渲染完成才能访问
- 选项是 `<a>` 标签，不是 `<li>` 或 Ant Design 菜单项
- 点击选项后可能弹出 Ant Design Modal（如批量改图片尺寸）→ 此时 DOM 操作切换回主文档

### CKEditor 面板 vs Ant Design Modal 的分界线

操作流程从 CKEditor 面板切换到 Ant Design Modal 时，DOM 操作对象切换：
- **CKEditor 面板** → 操作 `cke_panel_frame` 中的内容（通过 `frame_locator`）
- **Ant Design Modal** → 操作 `.ant-modal-content` 中的内容
- Ant Design Select 下拉 → portal 到 body 级别，用 `.ant-select-dropdown` 查找

### 产品图片批量改尺寸完整流程（2026-06-11 全流程验证）

```python
# Step 1: 点击 CKEditor 工具栏的"批量编辑图片" combo
page.evaluate("""() => {
    var combo = document.querySelector('.cke_combo__batcheditimgdropdow .cke_combo_button');
    if (!combo) {
        var all = document.querySelectorAll('.cke_combo_button');
        for (var i = 0; i < all.length; i++) {
            if (all[i].innerText.trim() === '批量编辑图片') { combo = all[i]; break; }
        }
    }
    if (combo) combo.click();
}""")
time.sleep(3)

# Step 2: 通过 iframe 中的 a 标签点"批量改图片尺寸"
panel = page.frame_locator('iframe.cke_panel_frame')
for i in range(panel.locator('a').count()):
    if '批量改图片尺寸' in panel.locator('a').nth(i).inner_text():
        panel.locator('a').nth(i).click()
        break
time.sleep(3)

# Step 3: 设置尺寸 800px
page.evaluate("""() => {
    var inputs = document.querySelectorAll('.ant-modal input');
    for (var inp of inputs) {
        if (inp.offsetParent !== null) {
            var ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            ns.call(inp, '800');
            inp.dispatchEvent(new Event('input', {bubbles: true}));
            break;
        }
    }
}""")
time.sleep(1)

# Step 4: 选择全部
page.evaluate("""() => {
    var all = document.querySelectorAll('.ant-modal button, .ant-modal span, .ant-modal div');
    for (var i = 0; i < all.length; i++) {
        if (all[i].offsetParent !== null && all[i].textContent && all[i].textContent.trim() === '选择全部') {
            all[i].click(); return;
        }
    }
}""")
time.sleep(1)

# Step 5: 生成JPG
page.evaluate("""() => {
    var all = document.querySelectorAll('.ant-modal button, .ant-modal span, .ant-modal div');
    for (var i = 0; i < all.length; i++) {
        if (all[i].offsetParent !== null && all[i].textContent && all[i].textContent.trim() === '生成JPG图片') {
            all[i].click(); return;
        }
    }
}""")
time.sleep(3)
```

---

## 四、常见坑点汇总

| 症状 | 原因 | 修复 |
|:--|:--|:--|
| 引用模板弹窗打开了但选不中 | checkbox 在操作列第4个 td 中 | 用 `el.querySelector('tr')` 找到行，再找最后一个 td 中的 checkbox（`.ant-checkbox-wrapper`）|
| 引用模板弹窗堆叠了3层 | 连续点了多次「引用模板」 | 先遍历 `.ant-modal-close` 关闭所有弹窗，再重新点「引用模板」 |
| 批量改图片尺寸按钮找不到 | CKEditor 面板用 iframe 渲染 | 通过 Playwright `frame_locator('iframe.cke_panel_frame')` 访问 |
| 批量改图片尺寸按钮找到了但点不到 | iframe 未完全渲染 | 点击 combo 后等待 3 秒再访问 iframe |
| 批量改图片尺寸 Modal 中的下拉点不开 | Ant Design Select 在 modal 中 | 用 `page.mouse.click(x, y)` 坐标点击而非 JS evaluate |
| 生成了但图片尺寸没变 | 没点「选择全部」只点了单个图片 | 步骤：设800 → 选全部 → 生成JPG，顺序不能错 |
| Ant Select 下拉不显示 | portal 渲染在 body 级别，不在 modal 内 | 用 `document.querySelectorAll('.ant-select-dropdown')` 全局搜索 |
| 无线端编辑器不显示 | radio 已 checked 但容器 `display: none` | 先切到老版编辑器再切回来 |
| 生成JPG报"请选择图片" | 没点「选择全部」就点生成了 | 先选图片再生成 |
| CKEditor API 访问不到 | 编辑器未完全初始化 | 确保 editor 容器 `display: block` 后再访问 |
| 无线端弹窗无限堆叠 | 弹出「确定关闭？」后点了「关闭」而非「确 定」 | 确认窗打开后必须点「确 定」或「取 消」，不能继续点「关闭」 |
| 无线端一键生成无反应 | 按钮被工具栏遮挡或容器未激活 | 先用 CKEditor API fallback 复制内容，再点橙色「保存」 |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*