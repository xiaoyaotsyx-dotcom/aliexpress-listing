# Ant Design Select 共享池污染 — 诊断与修复

> 2026-06-15/16 发现于店小秘编辑页
> 影响：电压(Voltage)和功率(瓦)(Power (W)) 两个必填属性

## 现象

在多次操作 Ant Design Select 下拉后，**某些 Select 永久失效**——无论用 mouse.click、keyboard.type、locator.click、dispatchEvent，选项点了但值不提交。

**典型表现：**

| 检查项 | 正常 Select（如品牌） | 污染 Select（如电压） |
|:--|:--|:--|
| `ant-select-selection-item` | ✅ 有值（如 NONE(NONE)） | ❌ 为空 |
| 搜索输入框 value | 空 | 有残留（如"110 V"或"1w"） |
| 下拉选项 | 能找到 | 能找到，也能「点中」 |
| 点击后验证 | ✅ 值变了 | ❌ 还是空 |
| 搜索框清空后 | 正常 | 选项消失（虚拟滚动不渲染） |

### 🆕 2026-07-03 补充：非污染场景的「选项极少」失败

还有一种失败场景 **不是共享池污染**，而是 antd Select 选项极少（2-3个）时的固有行为：

**受影响属性：** 材质(Material=塑料/不锈钢)、是否包含电池(Battery Included=是/否)、电源(Power Source=USB/其他)

**与污染的区别：**
| 特征 | 共享池污染 | 选项极少缺陷 |
|:--|:--|:--|
| 搜索框残留 | ✅ 有（如"110V"） | ❌ 无 |
| 下拉可见选项 | 混入其他属性的选项（>20个） | 仅本属性的2-3个选项 |
| 点击选项后 | `ant-select-selection-item` 仍为空 | 同左 |
| 根本原因 | 共享 Portal 内部状态错乱 | React 合成事件系统不接受 click |
| 修复 | 开新标签页 | 唯一修复：用户手动操作浏览器 |

**共同结论：** 无论污染还是极少数选项，CDP/Playwright 自动化在 antd Select 上均有死区。尝试3次无效后直接告知用户。

## 诊断方法

```python
# 在 Playwright 中检查是否污染
check = page.evaluate("""() => {
    var items = document.querySelectorAll('.ant-form-item');
    for (var item of items) {
        var label = item.querySelector('.ant-form-item-label label');
        if (!label) continue;
        var txt = label.textContent.trim();
        if (txt.includes('电压') || txt.includes('功率')) {
            var selItem = item.querySelector('.ant-select-selection-item');
            var searchInput = item.querySelector('input[type=search]');
            return {
                label: txt.substring(0, 15),
                selectionItem: selItem ? selItem.textContent.trim() : '(空)',
                searchValue: searchInput ? searchInput.value : 'N/A',
                disabled: item.querySelector('.ant-select')?.classList.contains('ant-select-disabled')
            };
        }
    }
    return 'not found';
}""")
# 如果 selectionItem 为空但 searchValue 有残留 → 已污染
```

## 根本原因

店小秘使用 **Vue 3 + Ant Design Vue**。所有 Select 共享同一个下拉 Portal（`<body>` 尾部）。反复开/关/点选导致 Portal 内部的 Reactivity 状态机错乱：

1. 每次打开 Select A，Portal 渲染 A 的选项
2. 选择选项，Portal 告诉 Select A「值变了」
3. 关闭 Portal
4. 但 Portal 内部的 `activeValue` 映射可能指向了 Select B
5. 后续操作 Select C → 选项显示 C 的 → 点选 → 值写给了 Select B

经过多次交错操作后，电压和功率的 Select 实例内部状态完全错乱，**任何外部交互都无法修复**。

## 修复方案

### 方案A（推荐）：开新标签页

```python
# 不要在污染页面上继续尝试！
page = ctx.new_page()
page.goto(f'https://www.dianxiaomi.com/web/smt/edit?id={PRODUCT_ID}')
time.sleep(5)

# 🏆 先填最容易出问题的两个！
fill_select(page, '电压(Voltage)', 'DC5V')
fill_select(page, '功率(瓦)(Power (W))', '1瓦')
# 再填其他（现在共享池是干净的）
fill_select(page, '品牌(Brand Name)', 'NONE')
fill_select(page, '风量(Air Volume)', '50')
# ...
```

### 方案B：手动清空 + 重试（成功率约30%）

```python
# 1. 清空搜索输入框
page.evaluate("""() => {
    var items = document.querySelectorAll('.ant-form-item');
    var targets = ['电压', '功率'];
    items.forEach(function(item) {
        var label = item.querySelector('.ant-form-item-label label');
        if (!label) return;
        for (var t of targets) {
            if (label.textContent.includes(t)) {
                var inp = item.querySelector('input[type=search]');
                if (inp && inp.value) {
                    var ns = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value').set;
                    ns.call(inp, '');
                    inp.dispatchEvent(new Event('input', {bubbles: true}));
                }
            }
        }
    });
}""")
# 2. 打开下拉，用 keyboard.type 搜索（真实键盘事件触发 React onChange）
page.keyboard.type('DC5V')
time.sleep(2)
# 3. ArrowDown + Enter
page.keyboard.press('ArrowDown')
page.keyboard.press('Enter')
```

### 预防措施

1. **先在干净的共享池上填电压和功率**（最容易出问题的优先）
2. 填属性不要回头反复操作同一个 Select
3. 每个 Select 只打开一次、选一次、关闭
4. 如果连续 3 次尝试都失败 → **停止尝试** → 汇报用户

## 经验教训（2026-06-16）

- 第一次填所有 7 个必选属性成功了（因为那是第一次操作页面，共享池是干净的）
- 浏览器刷新（browser_navigate）后电压和功率就再也填不上了
- 在同一个页面上重复尝试各种方法（mouse.click ×3、keyboard ×2、locator ×1、dispatchEvent ×2、CDP ×1）全都无效
- **不要在同一个问题上打转超过 5 分钟**——用户会说"不要总在原地打转"

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*