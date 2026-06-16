# 海关监管属性填写指南

> 店小秘编辑页「模版信息」tab → 海关监管属性 → 添加海关监管 弹窗的完整操作。

## 弹窗结构

点击「添加海关监管」按钮后，弹出一个 Ant Design Modal，结构如下：

```
┌─ 海关监管 ──────────────────────────────┐
│                                           │
│ 您的产品将基于您填写的海关监管属性...      │
│                                           │
│ 品名(Product name): [请选择 ▾]            │
│                                           │
│                    [取消]  [确定]          │
└───────────────────────────────────────────┘
```

## JS 操作步骤

### 1. 点击「添加海关监管」按钮

```javascript
const btns = document.querySelectorAll('button.ant-btn-primary');
for (const btn of btns) {
  if (btn.textContent.trim() === '添加海关监管') {
    btn.scrollIntoView({block: 'center'});
    btn.click();
    break;
  }
}
```

### 2. 打开品名下拉

```javascript
// 等弹窗渲染
await new Promise(r => setTimeout(r, 500));

const modal = document.querySelector('.ant-modal');
const selects = modal.querySelectorAll('.ant-select-selector');
for (const sel of selects) {
  if (sel.textContent.includes('请选择') || sel.textContent.includes('品名')) {
    sel.click();
    break;
  }
}
```

### 3. 选择品名选项

```javascript
await new Promise(r => setTimeout(r, 600));

const opts = document.querySelectorAll('.ant-select-item-option');
for (const opt of opts) {
  if (opt.offsetParent !== null && opt.textContent.includes('空气净化器')) {
    opt.click();
    break;
  }
}
```

### 4. 点击确定

```javascript
const modal = document.querySelector('.ant-modal');
const btns = modal.querySelectorAll('button');
for (const btn of btns) {
  if (btn.textContent.trim() === '确定') {
    btn.click();
    break;
  }
}
```

## 品名选项

| 选项 | 推荐度 | 说明 |
|:--|:--:|:--|
| **空气净化器(Air Purifier)** | ✅ 最推荐 | 与产品分类「空气净化器」一致 |
| 净化器(purifiers) | ⚠️ 次选 | 名称不完整 |
| 空气清新项链(air cleaning necklace) | ❌ 不推荐 | 描述性名称，非标准海关品名 |

## 验证

- 弹窗关闭 = 操作成功
- 关闭后海关监管属性区应显示已选的品名文本
- 可以在页面上查看到「海关监管属性」区域是否有新出现的内容

## 坑点

- ⚠️ 「添加海关监管」按钮有多个匹配 `ant-btn-primary` 的元素，必须精确匹配文本
- ⚠️ 弹窗打开后需要等待渲染（~500ms），不能立即操作下拉
- ⚠️ 弹窗内的 placeholder 文本「请选择」可能与其他下拉混淆，需限定在 `.ant-modal` 内查找
- ✅ 品名下拉只有 3 个选项，不会分页
- ✅ 不需要填其他字段，选完品名直接确定即可

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*