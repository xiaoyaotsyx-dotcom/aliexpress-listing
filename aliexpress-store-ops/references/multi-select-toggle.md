# Ant Design Multi-Select: Toggle Individual Options

## 适用场景

店小秘中部分属性是 **多选模式**（`ant-select mode="multiple"`），即一个字段可以选多个值。典型例子：

- **高关注化学品(High-concerned chemical)** — 需要只选「天然未处理(None)」，去掉其他所有

## 多选组件的特点

1. 下拉打开后，所有选项都是**可见的可点击项目**
2. 点击**已选中的选项**会**取消选中**（toggle off）
3. 点击**未选中的选项**会**选中它**（toggle on）
4. 各选项间**互不冲突**（可以同时选中多个）

## 操作流程

```python
# 1. 鼠标坐标点击打开 Ant Select 下拉
coord = page.evaluate("""() => {
    var items = document.querySelectorAll('.ant-form-item');
    for (var i = 0; i < items.length; i++) {
        var label = items[i].querySelector('.ant-form-item-label label');
        if (label !== null && label.textContent.indexOf('高关注化学品') !== -1) {
            var sel = items[i].querySelector('.ant-select-selector');
            if (sel) {
                sel.scrollIntoView({block: 'center'});
                var r = sel.getBoundingClientRect();
                return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
            }
        }
    }
}""")
page.mouse.click(coord['x'], coord['y'])
time.sleep(2)

# 2. 获取所有可见选项及其选中状态
opts = page.evaluate("""() => {
    var opts = document.querySelectorAll('.ant-select-item-option');
    var info = [];
    for (var i = 0; i < opts.length; i++) {
        if (opts[i].offsetParent !== null) {
            var cls = opts[i].className;
            info.push({
                idx: i,
                text: opts[i].textContent.trim(),
                selected: cls.indexOf('selected') !== -1 || cls.indexOf('option-selected') !== -1
            });
        }
    }
    return info;
}""")

# 3. 按需 toggle 每个选项
for o in opts:
    text = o["text"]
    should_select = '天然' in text or 'None' in text  # 想保留的
    is_selected = o["selected"]
    
    if should_select != is_selected:  # 当前状态和目标状态不一致时需要点
        page.evaluate("""idx => {
            var opts = document.querySelectorAll('.ant-select-item-option');
            if (opts[idx] !== null && opts[idx].offsetParent !== null) {
                opts[idx].click();
            }
        }""", o["idx"])
        time.sleep(0.5)

# 4. 关闭下拉
page.keyboard.press('Escape')
```

## 关键点

- **不要尝试找"删除"按钮**（×图标）来删除已选项——多选的 × 图标只在某些版本可用
- 直接在打开的下拉**点击已选项进行 toggle** 更可靠
- `className` 中包含 `selected` 或 `option-selected` 表示该选项**当前已被选中**
- 对不需要的选项，点击它会取消选中（toggle off）
- 对需要的选项，如果未选中则点击它会选中（toggle on）

## 场景示例

| 目标 | 初始状态 | 操作 |
|:--|:--|:--|
| 只保留 天然未处理(None) | 已选：A-alpha-C + 乙酰异羟肟酸 + 天然未处理 | 点 A-alpha-C (取消) → 点 乙酰异羟肟酸 (取消) → 天然未处理保留 |
| 只保留 天然未处理(None) | 已选：天然未处理(None) + 其他 | 点其他每个已选项取消，天然保留 |
| 只保留 天然未处理(None) | 未选任何 | 点 天然未处理 选中即可 |

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*