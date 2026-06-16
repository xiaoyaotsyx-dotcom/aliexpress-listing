# CDP ant-select 下拉残留修复（2026-06-14 实战验证）

## 问题

通过 CDP `Input.dispatchKeyEvent` 发送 Escape 键无法关闭 ant-design 的 select dropdown。

### 验证过程

1. 填了3个属性后（产地/品牌/高关注化学品）
2. 发送2次 Escape keyDown+keyUp 事件
3. 检查 `.ant-select-dropdown:not(.ant-select-dropdown-hidden)` → 仍有3个 dropdown 残留
4. 后续点击全部打在残留遮罩上，无效

## 解决方案

用 JS 直接添加 `ant-select-dropdown-hidden` 类：

```js
// 每次选中值后立即执行
document.querySelectorAll('.ant-select-dropdown').forEach(d => {
  d.classList.add('ant-select-dropdown-hidden');
});
```

## 完整操作模板

```js
// 模板：打开 → 选择 → 隐藏
// 1. CDP mousePressed+mouseReleased 在 ant-select-selector 坐标
// 2. Runtime.evaluate 选值
(() => {
  const drops = document.querySelectorAll('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
  for (const d of drops) {
    const items = d.querySelectorAll('.ant-select-item-option');
    for (const item of items) {
      if (item.textContent.includes('目标值')) {
        item.click();
        break;
      }
    }
  }
})();

// 3. Runtime.evaluate 隐藏
document.querySelectorAll('.ant-select-dropdown').forEach(d => {
  d.classList.add('ant-select-dropdown-hidden');
});
```

## 注意事项

- 这个方案是**绕过** CDP 限制，不是理想方案
- 组件内部状态可能不同步（Vue 认为 dropdown 仍打开），但实际使用无副作用
- 每次操作后必须执行隐藏，否则残留累积

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*