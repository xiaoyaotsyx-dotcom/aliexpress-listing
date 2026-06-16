---
name: dxm-attributes
description: 店小秘速卖通编辑页——属性信息模块：产品属性批量填（ant-select CDP填充）+ 自定义属性删除
domain: ecommerce
triggers:
  - 用户说"填属性"、"产品属性"、"属性信息"、"删自定义属性"
  - 店小秘编辑页打开后需要填属性信息
---

# 店小秘属性信息模块

## 环境

CDP browser_cdp 直连。编辑页 target_id 通过 `Target.getTargets` 获取。

## Step 1：切换到属性信息 tab

```
Runtime.evaluate:
  const links = document.querySelectorAll('.anchor-menu-item, a');
  for (const l of links) {
    if (l.textContent.trim() === '属性信息') { l.click(); break; }
  }
```

## Step 2：先开1688查参数（新标签页）

在填属性之前，需要从1688获取产品参数。

### 获取1688 URL
```
Runtime.evaluate (在编辑页 target):
  const links = document.querySelectorAll('a');
  for (const l of links) {
    if (l.href && l.href.includes('detail.1688.com')) return l.href;
  }
```

### 在新标签页打开1688
```
Target.createTarget: { url: 1688_URL }
```

### 提取1688参数
详见 `references/1688-json-extraction.md`：
- 嵌入JSON正则：`window.__INIT_DATA__` 或 `<script>` 内 JSON
- 页面文本提取：货号、重量、品牌、材质、产地

## Step 3：填写产品属性

### 🔴 铁律：先枚举所有星号字段再填，不要声称完成

**2026-07-18/19 血训（两次！）：** 
1. 填了5个属性就声称「模块3完成」→ 用户指出还有液晶显示、最大出餐量、最小出餐量、是否智能、是否包含电池全部没填。
2. 填了7/9就声称完成 → 用户："你怎么叫验证通过了呢？验证通过是要把所有带星号的选项都要填了，才能叫通过。"
**必须先用 DOM query 枚举 ALL 带星号字段，逐项验证填完，9/9才算通过。**

### 检测带星号字段（正确方式）

**类名是 `span.attr-label.required`，不是 `.ant-form-item-required`！**

```javascript
// 正确检测星号
labelEl.querySelector('span.attr-label.required')
```

```javascript
// 完整枚举所有星号字段及当前值
Array.from(document.querySelectorAll('#attrInfo .ant-form-item'))
  .filter(item => item.querySelector('span.attr-label.required'))
  .map(item => ({
    label: item.querySelector('label').innerText.trim(),
    value: item.querySelector('.ant-select-selection-item')?.textContent?.trim() || '(empty)'
  }));
```

### 铁律（按优先级）
1. **红色星号必填** — 必须选一个值
2. **有下拉选项的都选一个值** — 不能空着
3. **填空输入框不填** — 跳过
4. **1688有的参数按1688选最接近的值** — 无数据则跳过
5. **不知道选什么时选最接近的选项** — 选错用户会纠正

### 属性值速查

| 属性 | 来源 | 常用值 |
|:--|:--|:--|
| 产地 | 固定 | 中国大陆 |
| 省份 | 固定 | 浙江（义乌产） |
| 品牌 | 固定 | NONE |
| 材质 | 1688 | 硅胶→塑料(无硅胶选项时), 不锈钢, 尼龙等 |
| 高关注化学品 | 固定 | 天然未处理 |
| 类型 | 1688 | 狗狗/猫咪/通用 |
| 液晶显示 | 推断 | 无(No) — 宠物水杯无LCD |
| 最大出餐量 | 推断 | 选中间值（如水杯500g） |
| 最小出餐量 | 推断 | 选最小值（如水杯100g） |
| 是否智能 | 推断 | no(no) — 宠物水杯非智能 |
| 是否包含电池 | 推断 | no(no) — 宠物水杯无电池 |
| 电源 | 推断 | 无数据跳过 |
| 电压 | 1688 | 无数据跳过（共享下拉池重灾区） |
| 动力来源 | 推断 | 无数据跳过 |
| 承受重量 | 1688 | 无数据跳过 |
| 季节/特性 | 1688 | 无数据跳过（这些可能是空下拉） |

### CDP 操作：ant-select 下拉填充

**首选方案（下拉已初始化时）：JS强制显示 + 点击（2026-07-19 验证）**

⚠️ **此方案仅当dropdown已有option时有效。** 全新编辑页需先Playwright mouse.click打开每个下拉初始化option。

Playwright `mouse.click` 坐标法在此页面上**不可靠**（坐标偏移、dropdown不出现、CDP relay频繁断连）。
真正有效的方案是**纯JS操作**——找到含目标选项的dropdown → 强制显示 → 点击选项。Vue 3会自动拾取点击事件并更新组件状态。

```javascript
// 批量填充（通过 browser_cdp Runtime.evaluate 执行）
(function(){
  var targets = ['中国大陆(Origin)(Mainland China)', 'NONE(NONE)', '无(No)',
                  '500g(500g)', '100g(100g)', '塑料(Plastic)',
                  'no(no)', '天然未处理(None)', 'no(no)'];
  for (var t = 0; t < targets.length; t++) {
    var target = targets[t];
    var dds = document.querySelectorAll('.ant-select-dropdown');
    for (var i = 0; i < dds.length; i++) {
      var dd = dds[i];
      var items = dd.querySelectorAll('.ant-select-item-option');
      for (var j = 0; j < items.length; j++) {
        if (items[j].textContent.trim() === target) {
          dd.classList.remove('ant-select-dropdown-hidden');
          dd.style.display = '';
          dd.style.opacity = '1';
          dd.style.pointerEvents = 'auto';
          items[j].scrollIntoView({block: 'nearest'});
          items[j].click();
          items[j].dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
          items[j].dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
          break;
        }
      }
    }
  }
})()
```

⚠️ **批量填充陷阱：** 当多个dropdown同时被显示时，`no(no)` 这类重复选项会匹配到错误的dropdown。对于重复选项值，**必须逐个字段填充**，每次填充后关闭所有dropdown再填下一个。

⚠️ **Dropdown损坏陷阱（2026-07-19 发现）：** 对 dropdown 频繁执行 `dd.style.display='none'` + `dd.classList.add('ant-select-dropdown-hidden')` 会导致所有 dropdown 的 option 数量变为 0（`querySelectorAll('.ant-select-item-option').length === 0`）。**只能重新加载页面才能恢复。** 发现 0 items 时不要继续尝试——刷新页面重来。

⚠️ **批量填充后验证：** JS批量填充后必须逐字段验证。不要因为8/9就声称"完成"。用户对"验证通过"的定义是**所有带星号字段全部填完**。

**降级方案：Playwright坐标法（CDP relay正常时可用）**
```
1. 【点】获取 selector DOM 坐标，打开下拉
   Input.dispatchMouseEvent(type='mousePressed', x, y)
   Input.dispatchMouseEvent(type='mouseReleased', x, y)

2. 【选】匹配选项并点击
   Runtime.evaluate:
     const drops = document.querySelectorAll('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
     for (const d of drops) {
       d.querySelectorAll('.ant-select-item-option').forEach(item => {
         if (item.textContent.includes('目标值')) { item.click(); }
       });
     }

3. 【JS隐藏】强制关闭所有dropdown（Escape在CDP下无效！）
   Runtime.evaluate:
     document.querySelectorAll('.ant-select-dropdown').forEach(d => {
       d.classList.add('ant-select-dropdown-hidden');
     });

4. 【移动】到下一个 select，重复步骤 1
```

### ⚠️ 为什么必须关闭dropdown（下拉残留陷阱 — 2026-06-14 实战验证）

ant-design 的 select dropdown 打开后**仍在 DOM 中且有一个透明遮罩**。如果不关闭，下一个 select 的 click 会打在遮罩上，完全无效。

**❗ CDP 下的关键发现：`Input.dispatchKeyEvent Escape` 无法关闭 ant-select dropdown。** 必须用 JS `classList.add('ant-select-dropdown-hidden')` 强制隐藏。

### ⚠️ 电压/功率是共享下拉池重灾区

店小秘的电压和功率字段共享同一个下拉数据池。如果连续 3 次选不上——**停手，开新标签页先填这两个字段**，不要死磕。

## Step 4：删除自定义属性

### 检测自定义属性是否存在

自定义属性的 DOM 结构不是 `.ant-tag`，而是 `div.custom-attr-item`。每行含两个 `<input>`（属性名/属性值）和一个关闭按钮。

**查询（browser_cdp Runtime.evaluate）：**
```javascript
(function(){
  var items = document.querySelectorAll('#attrInfo .custom-attr-item');
  var vals = [];
  items.forEach(function(a){
    var inputs = a.querySelectorAll('input');
    if (inputs.length >= 2) vals.push(inputs[0].value + '=' + inputs[1].value);
  });
  return JSON.stringify(vals);
})()
```

### 实测有效方法：Playwright locator 逐条删除（2026-07-19 验证）

**「批量操作→删除全部→确 定」路径未经实测验证。实际验证有效的方案是直接逐条点击关闭图标：**

```python
# Playwright（需 CDP relay 正常）
# 1. 滚动到自定义属性区域
await page.evaluate("document.querySelector('#attrInfo .smtCustomAttrs').scrollIntoView({block: 'center'})")

# 2. 获取自定义属性总数
count = await page.evaluate("document.querySelectorAll('#attrInfo .custom-attr-item').length")

# 3. 逐个点击关闭图标（.icon_close 类名，不是 .anticon-close！）
for i in range(count):
    close_btn = page.locator("#attrInfo .custom-attr-item .icon_close").first
    await close_btn.click(force=True, timeout=3000)
    await asyncio.sleep(0.3)

# 4. 验证
remaining = await page.evaluate("document.querySelectorAll('#attrInfo .custom-attr-item').length")
```

**⚠️ 关闭按钮类名是 `iconfont icon_close`，不是 `.anticon-close` 或 `.ant-tag-close-icon`！** JS `element.click()` 无效——Vue 组件需要 Playwright 真点击。

**❌ 已证伪的方法：**
- JS `element.click()` / `dispatchEvent('click')` → Vue 不认，删不掉
- `Input.dispatchMouseEvent` → 坐标难定位

## ⚠️ 已知坑点
1. **下拉残留** — 必须用 JS `classList.add('ant-select-dropdown-hidden')` 关闭，CDP Escape 无效！
2. **电压/功率共享池** — 卡3次就开新页
3. **JS click 对 antd 无效** — 必须用 Playwright 真点击（或对普通 select 用 JS 强制显示 dropdown + click）
4. **弹窗「确 定」有空格** — 用 `innerText.trim()` 而非 `textContent.trim()`
5. **填空输入框不填** — 1688无数据的输入框直接跳过
6. **同一操作不超3次** — 3次不成功停手汇报
7. **ant-select 坐标需精确定位** — 用 `item.querySelector('.ant-select-selector').getBoundingClientRect()`，不要用 label 坐标
8. **1688参数提取** — 用 `window.context` JSON（`productPackInfo.fields.pieceWeightScale`）+ 页面文本双路径
9. **🔧 auto-complete 型 select 填充方法** — 见上方专节
10. **🚨 CDP relay 断连（2026-07-19 发现）** — Playwright `connect_over_cdp('http://127.0.0.1:19223')` 偶发超时（3分钟超时），症状为所有后续 Playwright 操作全部失败。此时必须检修 relay 链路：`kill relay进程 → taskkill chrome → 重启Chrome(带--remote-debugging-port=9222) → 重启Relay2.exe → 重启WSL relay → 更新browser.cdp_url`。参考 `aliexpress-store-ops/references/chrome-cdp-relay.md` 检修脚本。
11. **Dropdown 损坏后只能刷页** — 对 dropdown 频繁 classList.add/remove 会导致 option count 归零。发现 0 items 时刷新页面重来（7个已填字段也会丢失）。
13. **🔴 属性下拉共享池乱串（2026-07-19新增——高频）：** `selector.click()` + `dispatchEvent(MouseEvent)` 能打开dropdown，但 `querySelectorAll('.ant-select-dropdown')` 可能返回错误字段的dropdown。表现：点品牌→dropdown显示产地选项，点最大出餐→dropdown显示液晶选项。**唯一有效缓解：** ①每次操作前 `classList.add('ant-select-dropdown-hidden')` 强制关闭所有dropdown ②用 `dds[dds.length-1]` 取最新打开的dropdown ③每字段等待1.5s以上让Vue渲染完毕。但即使遵守以上规则，成功率仍非100%。**如连续3个字段失败，放弃属性模块，先填其他模块，最后通知用户手动修正。** 属性字段是店小秘自动化中最脆弱的一环。
13. **🔴 JS强制显示dropdown在全新页面上无效（2026-07-19）：** 新鲜加载的编辑页上，ant-select的dropdown里还没有option元素（未初始化）。JS `dd.classList.remove('ant-select-dropdown-hidden')` 强制显示后 `querySelectorAll('.ant-select-item-option')` 返回空数组。**必须先Playwright `page.mouse.click(selector坐标)` 打开下拉 → option渲染到DOM → 再用JS或keyboard选值。** 此问题仅在首次填写时出现，之前填过的字段仍有option残留。

**✅ 唯一有效方法：Playwright keyboard.type() + 点击空白处 blur（不要按 Enter！）**

```
1. page.mouse.click(selector坐标) → 打开并聚焦
2. page.keyboard.press("Control+a") → 全选
3. page.keyboard.press("Backspace") → 清空
4. page.keyboard.type("300g", delay=40~80) → 逐字符键入
5. await asyncio.sleep(1.5) → 等 auto-complete 匹配
6. page.mouse.click(500, 100) → 点页面空白处 blur 提交（⚠️ 不能按 Enter！）
```

**🚨 关键坑：不能按 Enter！** Enter 会清空 auto-complete 的值。正确做法是点击页面其他地方让 input 失去焦点（blur），Vue 会在 blur 时提交值。

**验证 auto-complete：** 值存储在 `input.value` 中，**不在** `.ant-select-selection-item` 中。验证代码必须分别处理：
```javascript
const item = sel.querySelector('.ant-select-selection-item');
const inp = sel.querySelector('input');
const val = (item && item.textContent.trim()) || (inp && inp.value) || '';
const filled = val !== '' && !sel.querySelector('.ant-select-selection-placeholder')?.offsetParent;
```

**❌ 已证伪的方法：**
- `nativeInputValueSetter` + `dispatchEvent('input')` → 值不持久化
- JS 强制显示 dropdown + click 选项 → Vue 不认
- `keyboard.type()` + `keyboard.press("Enter")` → 值被清空
- `keyboard.press("Tab")` → 提交裸字符串，不带括号部分（如 "300" 而非 "300g(300g)"）
- `document.execCommand('insertText')` → 值被组件截断

**⚠️ 中文输入：** `page.keyboard.press("塑")` 会报错 `Unknown key`。中文必须用 `page.keyboard.type("塑料")`。

已知 auto-complete 字段示例：最大出餐量、材质。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*