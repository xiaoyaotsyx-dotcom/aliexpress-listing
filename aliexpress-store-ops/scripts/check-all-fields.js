// 店小秘编辑页：扫描全部关注字段的当前值
// 在 CDP Runtime.evaluate 中执行
// 用法：先通过 Target.getTargets 找到 smt/edit 页面的 targetId
//       然后发送 Runtime.evaluate 执行此脚本

(function() {
    var items = document.querySelectorAll('.ant-form-item');
    var r = {};
    var targets = ['品牌','产地','材质','电池','电源','标题','容量','重量','尺寸',
                   '运费模板','服务模板','品牌制造商','海关','分类','报价','关税'];
    for (var i = 0; i < items.length; i++) {
        var lb = items[i].querySelector('.ant-form-item-label label');
        if (!lb) continue;
        var t = lb.textContent || '';
        var matched = targets.some(function(x) { return t.indexOf(x) !== -1; });
        if (!matched) continue;
        // 排除干扰匹配
        if (t.indexOf('品牌制造商') !== -1 && t.indexOf('品牌') !== -1) {
            // 保留 '品牌制造商' 但不匹配 '品牌' 时跳过
            if (t.indexOf('制造商') !== -1) {} // OK
        }
        if (t.indexOf('电池') !== -1 && t.indexOf('电源') !== -1) continue; // 电源匹配
        if (t.indexOf('净重') !== -1) continue;
        
        var selItem = items[i].querySelector('.ant-select-selection-item');
        var inp = items[i].querySelector('input:not([type=hidden]):not(.ant-select-selection-search-input)'); // 排除搜索框
        var ta = items[i].querySelector('textarea');
        var val = '';
        if (selItem) val = (selItem.title || selItem.textContent || '').trim();
        else if (inp) val = inp.value;
        else if (ta) val = ta.value;
        
        var key = t.replace(/[\\s\\n]/g, '').substring(0, 20);
        r[key] = val || '(empty)';
    }
    return r;
})()
