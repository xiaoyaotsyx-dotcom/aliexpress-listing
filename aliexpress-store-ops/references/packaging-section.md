# 包装信息填写指南

> 店小秘编辑页「包装信息」tab 的完整操作——包装后重量 + 包装后尺寸如何用 Hermes browser 工具（CDP 直连模式）填写。

## 包装区输入框定位

包装信息区在编辑页底部，有 4 个关键输入：

| 字段 | 定位方式 | 示例值 |
|:--|:--|:--|
| 包装后重量 | `document.getElementById('form_item_grossWeight')` | 0.045 |
| 包装后尺寸 长 | `document.querySelectorAll('.ant-input-status-error')[0]` | 6 |
| 包装后尺寸 宽 | `document.querySelectorAll('.ant-input-status-error')[1]` | 3 |
| 包装后尺寸 高 | `document.querySelectorAll('.ant-input-status-error')[2]` | 2 |

## 填入值的 JS 方法（Hermes browser_console / CDP evaluate）

**包装后重量：**
```javascript
const ns = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;

const wt = document.getElementById('form_item_grossWeight');
ns.call(wt, '0.045');
wt.dispatchEvent(new Event('input', { bubbles: true }));
wt.dispatchEvent(new Event('change', { bubbles: true }));
```

**包装后尺寸（长×宽×高）：**
```javascript
const ns = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
const sizeValues = ['6', '3', '2'];
const errInputs = document.querySelectorAll('.ant-input-status-error');
let i = 0;
for (const inp of errInputs) {
  if (inp.tagName === 'INPUT' && inp.type === 'text' && !inp.value) {
    ns.call(inp, sizeValues[i]);
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new Event('change', { bubbles: true }));
    i++;
    if (i >= 3) break;
  }
}
```

**验证方法：**
```javascript
// 查包装后重量
document.getElementById('form_item_grossWeight').value

// 查长宽高（error 状态消失 = 填对了）
// 填之前 class 含 ant-input-status-error，填后变为 ant-input-status-success
```

## 操作顺序（重要）

**⚠️ 必须按以下顺序操作，顺序颠倒会导致重复工作：**

1. **先** 在 SKU 表（全部颜色区）中填好每个 SKU 的 **重量(kg)** 和 **包装尺寸(cm)**
2. **再** 到包装信息区，填 **包装后重量** 和 **包装后尺寸**，值必须与 SKU 表完全一致
3. 如果先填了包装信息区再去改 SKU 表，包装信息区不会自动同步，需要回头再改一次

## 与 SKU 表一致性要求（用户强制规则）

**这四个字段是同一数据的两个副本：**

- 包装信息区的 **包装后重量**(kg)  =  SKU 表（全部颜色）的 **重量(kg)** 列
- 包装信息区的 **包装后尺寸**(cm)  =  SKU 表（全部颜色）的 **包装尺寸(cm)** 列

**填写规则：**
- 所有颜色 SKU 的库存重量和包装尺寸必须相同（共用同一个包装规格）
- 包装信息区的值必须与 SKU 表值完全一致（一位数都不能差）
- 不一致会导致物流运费计算错误，影响买家运费和产品转化

## 坑点

- ⚠️ 包装区 inputs 没有 `placeholder` 属性或 `id`（除重量外），只能通过错误状态类名 `ant-input-status-error` 定位
- ⚠️ 必须先滚动到包装区让输入框出现在视口内（`browser_scroll(down)` 多次），否则 input 的 `offsetParent` 可能为 null
- ⚠️ `nativeInputValueSetter` + `dispatchEvent('input')` 对 Ant Design Form Item **有效**（与此相对的，VXE Table 单元格需要键盘模拟）
- ✅ 填入后 Ant Design 自动验证并清除错误提示（`ant-input-status-error` → `ant-input-status-success`）

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*