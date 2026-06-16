# myj-table SKU 批量填充操作指南

> 2026-07-17 发现：店小秘使用 myj-table（非 vxe-table）作为 SKU 定价/库存表。
> 编辑页「产品信息」tab 包含 3 个并列的 myj-table，table[2] 是所有定价/库存列的所在地。

## 三表结构

| 表 | CSS 选择器 | 内容 | 列数 |
|:--:|:--|:--|:--:|
| table[0] | `.myj-table:nth-child(1)` | 颜色 + 自定义名称 + 图片 | 3列 |
| table[1] | `.myj-table:nth-child(2)` | 尺寸 + 自定义名称（通常为空） | 2列 |
| **table[2]** | `.myj-table:nth-child(3)` | **💰 所有定价/库存/重量/尺寸列** | **21列** |

## table[2] 结构

table[2] 包含 2 行表头 + 数据行：

1. **批量行**（第一行 `tr`）：输入框 + 下拉 + 批量填充按钮
2. **列名行**（第二行 `tr`）：字段标签
3. **数据行**（`tbody tr`）：每个 SKU 的实际数据

## 批量填充操作（推荐）

用 JS 一次性填批量行所有字段，然后点批量填充按钮：

```javascript
const t = document.querySelectorAll('.myj-table')[2];
if (!t) return;

// 1. 填所有输入框
var inps = t.querySelectorAll('input');
var vals = {
  '零售价': '1.30',
  '货值': '1.30',
  '库存': '2000',
  '重量': '0.1',
  '长': '8',
  '宽': '5',
  '高': '15'
};
for (var inp of inps) {
  if (inp.placeholder && vals[inp.placeholder]) {
    var s = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    s.call(inp, vals[inp.placeholder]);
    inp.dispatchEvent(new Event('input', {bubbles: true}));
    inp.dispatchEvent(new Event('change', {bubbles: true}));
  }
}

// 2. 设置 是否原箱 = 否
var selects = t.querySelectorAll('select');
for (var sel of selects) {
  var opts = sel.querySelectorAll('option');
  for (var opt of opts) {
    if (opt.value === '0') {
      sel.value = '0';
      sel.dispatchEvent(new Event('change', {bubbles: true}));
    }
  }
}

// 3. 点击批量填充
var btns = t.querySelectorAll('button');
for (var btn of btns) {
  if (btn.textContent.includes('批量填充')) {
    btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
  }
}
```

## 验证数据行

```javascript
const t = document.querySelectorAll('.myj-table')[2];
const rows = t.querySelectorAll('tbody tr');
Array.from(rows).map(row => {
  const inps = row.querySelectorAll('input');
  return Array.from(inps).map(inp => ({
    placeholder: inp.placeholder,
    value: inp.value
  }));
});
```

## 批量行字段映射

| 列索引 | 输入类型 | placeholder | 填写值 |
|:--:|:--|:--|:--:|
| 1 | input | 零售价 | 1.30 (成本价，零售价=货值) |
| 2 | input | 货值 | 1.30 (1688批发价) |
| 5 | input | 库存 | 2000 (封顶) |
| 6 | input | 重量 | 0.1 (1688参数) |
| 7 | input ×3 | 长/宽/高 | 8/5/15 |
| 8 | select | — | 0 (否) |

## 常见问题

- **批量填充按钮 disabled**：最少填一个字段按钮才会变可用
- **nativeInputValueSetter 不触发 Vue 更新**：必须 dispatch input + change 事件。dispatchEvent('input') 和 dispatchEvent('change') 缺一不可
- **批量填充后验证行数据**：用上述 JS 验证方法，不要刷新页面

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*