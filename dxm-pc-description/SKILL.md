---
name: dxm-pc-description
description: 店小秘速卖通编辑页——描述信息模块：PC端描述（CKEditor 引用模板 + 批量改图片尺寸 + 图片翻译）
domain: ecommerce
triggers:
  - 用户说"描述信息"、"PC端描述"、"CKEditor"、"引用模板"、"批量编辑图片"
  - 店小秘编辑页描述信息 tab 需要处理
---

# 店小秘PC端描述模块

## 环境

CDP browser_cdp 直连。CKEditor 在 iframe 内或页面内，需先定位。

## 切换位置

描述信息 tab → PC端描述（CKEditor 富文本编辑器）

## 子步骤

```
8.5a. 引用模板 → 选模板 → 选择
8.5b. 批量改图片尺寸（7步铁序）
8.5c. 图片翻译（中文→英文）
```

## Step 8.5a：引用模板

### CDP 操作
```
1. 切换到描述信息 tab
   Runtime.evaluate:
     const items = document.querySelectorAll('.anchor-menu-item');
     items.forEach(i => { if (i.textContent.trim() === '描述信息') i.click(); });

2. 等 2 秒 CKEditor 加载

3. 点 CKEditor 工具栏「引用模板」
   Runtime.evaluate:
     // 找按钮（可能需要精确选择器）
     const btns = document.querySelectorAll('.cke_button__templates, [title*="模板"], [title*="Template"]');
     btns[0].dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
     btns[0].dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
     btns[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));

4. 等弹窗 → 选模板 → 点「选择」
```

## Step 8.5b：批量改图片尺寸（✅ 2026-07-19 验证）

### 🔴 images-options 栏默认隐藏——必须 JS 强制显示

`.images-options` 由 Vue 3 控制显示/隐藏，正常情况永远不出现。**唯一有效方式：JS 强制设置 CSS 属性。**

```python
await page.evaluate('''() => {
    const io = document.querySelector('.images-options');
    if (!io) return;
    // 显示整条父链
    let el = io;
    while (el && el !== document.body) {
        el.style.setProperty('display', 'block', 'important');
        el.style.setProperty('visibility', 'visible', 'important');
        el.style.setProperty('opacity', '1', 'important');
        el = el.parentElement;
    }
    // 固定到视口可见位置
    io.style.setProperty('position', 'fixed', 'important');
    io.style.setProperty('top', '450px', 'important');
    io.style.setProperty('left', '800px', 'important');
    io.style.setProperty('z-index', '99999', 'important');
}''')
```

### 操作流程（4步）

```
1. 强制显示 images-options → 固定到 (800, 450)
2. page.mouse.click → 打开「批量编辑图片」下拉
3. 选「批量改图片尺寸」
4. 弹窗中：填 valueW=800 → 点「生成JPG图片」
   如点不动，用 JS element.click() 兜底
```

### 🔴 两个「批量编辑图片」陷阱
- **CKEditor 原生 combo**（`.cke_combo__batcheditimgdropdownlist`）→ 空面板 ❌
- **images-options 区的 ant-dropdown-trigger** → 正确入口 ✅

## Step 8.5c：图片翻译（✅ 2026-07-19 验证）

### 相同入口：images-options → 批量编辑图片 → 图片翻译

### 弹窗内操作（🔑 关键：一键翻译按钮要点两次）

```python
# 1. 选全部
sel = 弹窗内 label.ant-checkbox-wrapper[textContent='选择全部']
page.mouse.click(sel_x, sel_y)

# 2. 第1次点一键翻译 span → 打开语言下拉 → 选「中文 → 英文」
page.mouse.click(span_x, span_y)          # 打开下拉
cn_en = 找可见的 '中文 → 英文' 菜单项
page.mouse.click(cn_en_x, cn_en_y)        # 选语言（不提交）

# 3. 第2次点一键翻译 span → 提交翻译！
page.mouse.click(span_x, span_y)          # 提交
```

提交后出现双弹窗：原弹窗 + 进度弹窗「已翻译成功N张图片」。
翻译完成后再出现确认弹窗 → JS `element.click()` 点「确认」关闭。

## ⚠️ 已知坑点
1. **images-options 默认隐藏（Vue 3 控制）** — 必须 JS 强制 `style.setProperty('display','block','important')` 整条父链 + 固定定位到视口内。不要浪费时间找「展开图片栏」按钮。
2. **两个同名「批量编辑图片」** — cke_combo（空面板）vs images-options（真菜单），只用后者。
3. **🔑 一键翻译要点两次** — 第1次选语言，第2次提交。不要用 Enter 键！不要点完语言就等！
4. **生成JPG/PNG 按钮被 ant-modal-wrap 拦截** — mouse.click 后弹窗不关，用 JS `element.click()` 兜底即可。
5. **「一键翻译」≠「快速翻译」** — 快速翻译是 checkbox 开关，一键翻译是提交按钮。
6. **PC描述图在 iframe 中** — 无法通过主页面 DOM 查询图片，但 images-options 操作在主页面进行，不受影响。
7. **翻译完成后需 JS click 确认** — 确认弹窗的「确认」按钮也不能用 mouse.click，用 JS `element.click()`。
8. **CDP Input.dispatchMouseEvent 不可用** — 统一用 Playwright `page.mouse.click()`。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*