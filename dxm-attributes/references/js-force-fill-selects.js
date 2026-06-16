// 店小秘属性信息批量填充 - JS强制显示下拉法
// 使用方式：通过 browser_cdp Runtime.evaluate 执行
// 日期：2026-07-19 验证有效（7/9字段一次成功）
// 已知限制：对 ant-select-auto-complete 型字段无效

// ============================================================
// 单字段填充
// ============================================================
(function fillOneField(targetText) {
  var dds = document.querySelectorAll('.ant-select-dropdown');
  for (var i = 0; i < dds.length; i++) {
    var dd = dds[i];
    var items = dd.querySelectorAll('.ant-select-item-option');
    for (var j = 0; j < items.length; j++) {
      if (items[j].textContent.trim() === targetText) {
        // 强制显示 dropdown
        dd.classList.remove('ant-select-dropdown-hidden');
        dd.style.display = '';
        dd.style.opacity = '1';
        dd.style.pointerEvents = 'auto';
        // 滚动并点击选项
        items[j].scrollIntoView({block: 'nearest'});
        items[j].click();
        items[j].dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
        items[j].dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
        return 'selected: ' + items[j].textContent.trim();
      }
    }
  }
  return 'not found';
})('中国大陆(Origin)(Mainland China)');

// ============================================================
// 批量填充（注意：重复值如 'no(no)' 会匹配到第一个dropdown）
// ============================================================
(function batchFill(targets) {
  var results = [];
  for (var t = 0; t < targets.length; t++) {
    var target = targets[t];
    var found = false;
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
          results.push(target + ': OK');
          found = true;
          break;
        }
      }
      if (found) break;
    }
    if (!found) results.push(target + ': NOT FOUND');
  }
  return JSON.stringify(results);
})([
  'NONE(NONE)',
  '无(No)',
  '500g(500g)',
  '100g(100g)',
  '塑料(Plastic)',
  'no(no)',
  '天然未处理(None)',
  'no(no)'
]);

// ============================================================
// 检测带星号字段（正确方式）
// ============================================================
(function listStarredFields() {
  return Array.from(document.querySelectorAll('#attrInfo .ant-form-item'))
    .filter(function(item) {
      return item.querySelector('span.attr-label.required');
    })
    .map(function(item) {
      var label = item.querySelector('label').innerText.replace(/\s+/g, ' ').trim();
      var valEl = item.querySelector('.ant-select-selection-item');
      var val = valEl ? valEl.textContent.trim() : '(empty)';
      return {label: label, value: val, filled: val !== '(empty)'};
    });
})();

// ============================================================
// 识别 auto-complete 型字段（这些字段无法用JS填充）
// ============================================================
(function detectAutocomplete() {
  var selects = document.querySelectorAll('#attrInfo .ant-select');
  var ac = [];
  for (var i = 0; i < selects.length; i++) {
    if (selects[i].classList.contains('ant-select-auto-complete')) {
      var label = selects[i].closest('.ant-form-item')
        .querySelector('label').innerText.trim().substring(0, 40);
      ac.push({idx: i, label: label});
    }
  }
  return ac;
})();
