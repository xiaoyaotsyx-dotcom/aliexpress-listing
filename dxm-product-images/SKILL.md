---
name: dxm-product-images
description: 店小秘速卖通编辑页——产品图片模块：主图选图 + 批量改尺寸800×800 + 图片翻译 + 营销图片一键生成 + 颜色SKU图处理
domain: ecommerce
triggers:
  - 用户说"产品图片"、"主图"、"改尺寸"、"图片翻译"、"营销图"、"SKU图"、"颜色图"
  - 店小秘编辑页产品信息 tab 需要处理图片
---

# 店小秘产品图片模块

## 环境

CDP browser_cdp 直连。

## 子步骤总览

```
7a. 主图选图（选6张主图）
7b. 批量改尺寸 800×800
7c. 图片翻译（中文→英文）
7d. 营销图片一键生成
7e. 颜色SKU：改英文名
7f. 颜色SKU图：改尺寸
7g. 颜色SKU图：翻译
7h. 容量（带星号必填）
```

## Step 7a：主图选图（选6张）

### 🔴 铁律：必须选6张，不能多也不能少

速卖通要求主图为6张。店小秘主图区默认最多保留6张。从1688导入的图片通常超过6张，需要筛选出最佳6张。

### 选图规则（按优先级）
1. **白底图优先** — 纯白/浅色背景的产品图
2. **清晰度高** — 分辨率高，产品占比大
3. **多角度** — 正面、侧面、细节、使用场景各一张
4. **无中文文案** — 避免含大段中文的图（翻译可能失败）
5. **无水印** — 避免1688水印图

### 操作流程
1. 切换到「产品信息」tab
2. 在「产品图片」区，查看当前选用张数：
```javascript
// 检查选中张数
var items = document.querySelectorAll('.single-image');
var count = 0;
items.forEach(function(item) {
    if (item.querySelector('.ant-checkbox-wrapper-checked')) count++;
});
// 或直接读提示文案：
var tip = document.querySelector('.explain-module');
// → 「主图最多选用 6 张，已经选用了 5 张」
```
3. 如不足6张，点击下一个未选中图片的 checkbox：
```javascript
var items = document.querySelectorAll('.single-image');
for (var i = 0; i < items.length; i++) {
    if (!items[i].querySelector('.ant-checkbox-wrapper-checked')) {
        items[i].querySelector('input[type=checkbox]').click();
        break;  // 只加1张
    }
}
```
4. 验证提示变为「已经选用了 **6** 张」
5. 如需换图：先取消勾选，再勾选新图
6. 拖拽排序：首图为白底正面主图

## Step 7b：批量改尺寸 800×800

### 操作
1. 在产品图片区找到「crop编辑图片」链接 → 点击展开 dropdown
2. 下拉菜单选「批量改图片尺寸」
3. 弹窗中：
   - 选择1：「等比例调整」（默认）
   - 选择2：「图片小边」（默认）
   - 宽度输入框 name="valueW"：填入 800
   - （无独立高度输入框——等比例自动计算）
4. 点「生成JPG图片」

### ⚠️ 弹窗结构（2026-07-19 实测）
- 4个 ant-select 下拉（已预选"等比例调整"/"图片小边"等默认值）
- 1个 text input `name="valueW"`（宽度）
- 2个 checkbox（等比缩放相关，默认已勾选）
- 按钮：「生成JPG图片」「生成PNG图片」
- **没有「选择全部」步骤**——默认处理所有产品图片
- JS click 即提交，无进度条——modal 关闭 = 已提交后台处理

## Step 7c：图片翻译（中文→英文） — 主图6张 + SKU图

### 🔴 铁律：6张主图必须全部翻译
每条listing的6张主图都要做图片翻译。不能只点一次就跳过。

### ✅ 正确路径：页面顶部「一键翻译」按钮（2026-07-19 验证通过）

**唯一有效路径**：页面顶部工具栏的「一键翻译」按钮（button.ant-btn-default.translation-btn，y≈100）

```
1. 滚动到页面顶部 page.evaluate('window.scrollTo(0, 0)')
2. 找按钮：document.querySelectorAll('button') → textContent === '一键翻译' → getBoundingClientRect().top < 200
3. page.mouse.click(x, y) 打开弹窗（此步 CDP 可触发）
4. 弹窗显示：图片翻译 | 中文-英文 | 22张(全量) | 译图/原图 | 保留原图 | 强制识别
5. 点「确认」按钮提交 — ⚠️ 见下方坑点
```

### 🔑 「一键翻译」按钮操作（关键！2026-07-19 验证）

弹窗底部的「一键翻译」是 ant-dropdown-trigger 分裂按钮。**必须点两次：**

```
1. 点 span 文字区 → 打开下拉 → 选「中文 → 英文」（选语言，不提交）
2. 再点一次 span 文字区 → 提交翻译！
```

```python
span = (1993, 1061)  # 坐标每次实时 getBoundingClientRect() 获取

# 第1次：选语言
page.mouse.click(span_x, span_y)           # 打开下拉
cn_en = 找可见的 '中文 → 英文' 菜单项
page.mouse.click(cn_en_x, cn_en_y)         # 选语言

# 第2次：提交
page.mouse.click(span_x, span_y)           # 提交！
```

提交后出现双弹窗：原弹窗 + 「提示：状态：进行中... 已翻译成功N张图片」。

### ❌ 已证伪
- ~~Enter 键提交~~ — 不稳定，部分弹窗无效
- ~~点一次后直接 Enter~~ — 只在特定弹窗有效
- **统一使用「点两次 span」策略**
- **策略3**：JS `element.click()` — 对部分弹窗按钮有效（确认弹窗的「确认」按钮实测可用），但 crop 下拉弹窗的「一键翻译」分体按钮不响应。
- **策略4**（兜底）：用户手动点击 — 当以上全部失效时，如实告知用户，请用户手动点「确认」。不要重复尝试（本 session 验证：同一按钮尝试 3 次以上就是浪费）。

### ❌ 已证伪的路径
- **crop编辑图片 → 图片翻译 弹窗** — 该弹窗的「一键翻译」按钮是 ant-dropdown-trigger 分体按钮，必须先打开下拉选「中文→英文」再提交。下拉菜单项在 mouse 按下时即被关闭（antd click-away 机制），点击永远落不到菜单项上。**绝对不走这条路。**
- **JS dispatchEvent** — Vue 3 不响应合成事件，无效。
- **Playwright locator.click({force:true})** — modal 拦截 force 也无效（pointer-events 在 DOM 层被阻）。

### ⚠️ 注意
- 22张图（主图6张 + SKU颜色图全部）一次性全选并翻译
- 余额检查：弹窗底部显示「今日免费:N个 | 总秘豆:N个 | 可用图片翻译数量:N张」
- 余额为0时需充值，否则无法提交
- 提交后弹窗自动关闭，无进度条，后台异步处理
- 翻译结果需用户稍后检查（图片上的中文是否已变英文）

## Step 7d：营销图片一键生成

### 操作
1. 在营销图片区找「一键生成」按钮
2. 选择模板/场景
3. 生成 1:1 白底图 + 3:4 场景图

## Step 7e：颜色SKU改名

### 表结构
SKU颜色表（`document.querySelectorAll('table')[9]`）有3列：

| 颜色 | 自定义名称 (批量编辑) | 图片(无图可忽略)批量 |
|------|---------------------|---------------------|
| 白色 | 宠物户外喂水碗【绿色】 | 选择图片 |
| 黑色 | 宠物户外喂水碗【粉色】 | 选择图片 |

### ⚠️ 实测方法：通过「批量编辑」弹窗（2026-07-19）

**直接双击单元格编辑不可行**——Vue inline editor 的 input 接受值但不持久化（Enter/Tab/blur 均无法提交）。

**唯一有效路径：点表头「批量编辑」链接 → 弹窗「自定义属性编辑」**

弹窗内容：
- 每行一个 checkbox + 文本输入（对应每个SKU的自定义名称）
- 查找替换区：「被替换的内容」/「替换后的内容」
- 移除内容区：textarea

```
1. 点击 th 中「批量编辑」链接
2. 找到 placeholder="请输入" 的 input（每行一个）
3. fill("Green") / fill("Pink")
4. 可选：填「被替换的内容」= "宠物户外喂水碗【】" → 批量去前缀
5. 点「确定」
```

### ❌ 已证伪的方法
- 双击单元格 + fill + Enter → 值被清空
- 双击单元格 + fill + Tab → 值被清空  
- 双击单元格 + fill + 点空白处 blur → 值被清空
- JS nativeValueSetter + dispatchEvent → Vue 不认

## Step 7f：颜色SKU图改尺寸

### 路径
SKU颜色表 → 图片列 head 的「批量」链接 → 下拉 → 「批量改图片尺寸」 → 弹窗设置 800×800 → 生成JPG

### ⚠️ 关键：必须区分两个下拉
SKU图片区有两个外观相似的 action-link，下拉内容完全不同：
- **图片列 header 的「批量」链接**（`<a class="img-options-action-btn ant-dropdown-trigger">`）→ 下拉含「批量改图片尺寸」等10项操作
- **"批量编辑图片"链接** → 下拉只有5项（上传来源：本地/空间/网络/图片银行/采集），**不含**改尺寸/翻译

**区分方法：** 用 `textContent.trim() === '批量'` 且 parent 为 `<th>`（而不是 action-bar 中的 `批量编辑图片`）

### 正确的下拉完整菜单（10项）
```
本地图片 | 空间图片 | 网络图片 | 图片银行（速卖通）| 引用采集图片 | 批量改图片尺寸 | 批量编辑 | 图片翻译 | 图片白底 | 清空图片
```

### CDP 操作
1. 定位 SKU 颜色表 → 图片列 header → 点「批量」
2. 等 dropdown 出现 → 点「批量改图片尺寸」
3. 弹窗中 width=800 → 生成JPG

## Step 7g：颜色SKU图翻译

路径同 7f，但选「图片翻译」。仅含中文文案的图片需翻译。

## Step 7h：容量（产品信息 tab 带星号必填）

### 位置
产品信息 tab，y≈1000-1200 区域。标签「容量」，text input 类型。

### 数据来源
1688 产品页通常不含容量（ml）数据。需根据产品类型推断：
- 宠物饮水杯/碗：通常 300-500ml
- 用 `350ml` 作为默认值

### 填写方法
```javascript
const items = document.querySelectorAll('.ant-form-item');
for (const item of items) {
  if (item.querySelector('label')?.innerText.includes('容量')) {
    const inp = item.querySelector('input');
    const s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    s.call(inp, '350ml');
    inp.dispatchEvent(new Event('input', {bubbles: true}));
    inp.dispatchEvent(new Event('change', {bubbles: true}));
  }
}
```

## ⚠️ 已知坑点
1. **🔴 ant-modal-wrap 拦截所有自动化点击（2026-07-19 重大发现）** — 店小秘 Vue 3 弹窗的 `<div role="dialog" class="ant-modal-wrap">` 在 CDP 环境下会拦截所有 pointer events。Playwright `mouse.click()` / `locator.click({force:true})` / JS `element.click()` / `dispatchEvent` 全部无效。**表现为：按钮可定位、坐标正确、点击无报错，但弹窗不关闭、无任何反馈。** 遇到此情况直接告知用户手动点击，不要重复尝试（本 session 浪费 20+ 次点击）。此问题影响所有 ant-modal-wrap 弹窗内的按钮（图片翻译确认、批量改尺寸生成等）。
2. **「批量改图片尺寸」入口藏得深** — 需先点「crop编辑图片」→ 展开 dropdown → 选「批量改图片尺寸」。不要和「批量编辑」（另一个弹窗）混淆。
3. **CDP mouse 事件打不开 crop 编辑 dropdown** — `Input.dispatchMouseEvent` 无效，必须用 JS `element.click()` 打开。
4. **两个同名「批量编辑图片」按钮** — CKEditor combo vs antd dropdown，点错了用 Escape 关闭空面板
5. **ant-dropdown 绝对定位偏移到视口外** → 先 scroll 按钮到 y≈400-700
6. **Vue 3 不响应 JS dispatchEvent** → 用 JS `element.click()`（对 dropdown 有效）或 Playwright 真点击
7. **营销图一键生成无即时反馈** — modal 不弹，提交后静默处理
8. **SKU自定义名称不能双击编辑** — 单元格 inline edit 无法提交值。必须用表头「批量编辑」→ 弹窗修改。
9. **批量改尺寸弹窗没有独立高度输入** — 只有 `name="valueW"` 宽度，高度由「等比例调整」自动计算。没有「选择全部图片」步骤，默认全部处理。
10. **图片 resize/翻译/生成均为后台异步** — modal 关闭 = 已提交，无进度条，无完成通知。需用户稍后检查结果。
11. **🔴 主图必须选6张（2026-07-19 用户纠正）** — 页面提示「已选用N张」，如果是5张，必须再勾选1张凑满6张。速卖通要求6张主图，少1张都不行。
13. **🔑 翻译弹窗 Enter 键流程（2026-07-19 验证）** — 对 crop 下拉弹窗（分体按钮型），依次：选择全部 → 点「一键翻译」文字区 → 下拉选「中文→英文」→ 按 Enter → 弹窗变为「中文-英文 确认」→ 按 Enter 或 JS click 确认 → 弹窗关闭。Enter 键可以穿透部分 CDP 拦截。
14. **🔑 PC描述 images-options 强制显示技巧（2026-07-19）** — 描述信息 tab 的 `.images-options` 默认被 Vue 隐藏（`top: 0, visibility: hidden`），CKEditor iframe 中选图也不会触发显示。**唯一有效方法：JS force-show 整个祖先链 + Playwright mouse.click**：
    ```
    // 遍历 images-options 的所有祖先，强制 display:block
    let el = document.querySelector('.images-options');
    while (el && el !== document.body) {
        el.style.setProperty('display', 'block', 'important');
        el.style.setProperty('visibility', 'visible', 'important');
        el = el.parentElement;
    }
    // 固定到视口中央
    io.style.setProperty('position', 'fixed', 'important');
    io.style.setProperty('top', '450px', 'important');
    io.style.setProperty('left', '800px', 'important');
    io.style.setProperty('z-index', '99999', 'important');
    ```
    然后 `page.mouse.click()` 点 `.ant-dropdown-trigger` → 下拉正常出现 → 可选「批量改图片尺寸」「图片翻译」等。JS `element.click()` 无效（Vue 3 不认合成事件）。此技巧适用于 PC 描述图片的所有批量操作。
15. **页顶「一键翻译」按钮行为变更** — 当所有产品图片（主图+SKU图）已翻译后，页顶按钮不再弹窗（返回 no modal）。此按钮仅处理产品图片区，不含 PC 描述图片。PC 描述翻译必须走 images-options 路径。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*