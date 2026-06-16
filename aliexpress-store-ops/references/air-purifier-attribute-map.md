# 空气净化器（挂脖）品类属性索引映射表

> 适用于 店小秘 SPA 中「家用电器 > 生活家电 > 空气处理小家电 > 空气净化器」类目
> Ant Design Select 索引从页面加载时确定，随滚动和渲染可能偏移

## 已验证的 Ant Select 索引（按 Y 坐标排序，可见区域）

| 索引 | Y坐标(估) | 属性名 | 建议值 |
|:--:|:--:|:--|:--|
| 2 | 57 | 店铺名称 | [你的店铺名称]（已选） |
| 3 | 124 | **品牌(Brand Name)** | **NONE(NONE)** |
| 4 | 223 | **电压(Voltage)** | **5V(5V)**（USB设备） |
| 5 | 279 | **产地(Origin)** | **中国大陆(Mainland China)** |
| 6 | 341 | **风量(Air Volume)** | **50立方米/小时(50m³/h)** |
| 7 | 397 | **功率(Power (W))** | **1瓦(1w)** |
| 8 | 455 | **HEPA滤网等级** | **其他(Other)**（负离子款无滤网） |
| 9 | 513 | **高关注化学品** | **天然未处理(None)** |
| 10 | 586 | **噪音(Noise)** | **≤30分贝(≤30DB)**（1688标注36dB，选最接近的） |
| 11 | 790 | 尺寸(Dimensions) | 可选其他(Other) |
| 12 | 846 | **功能(Function)** | **杀菌功能(Sterilize)** |
| 13 | 902 | **安装方式(Installation)** | **便携式(Portable)** |
| 14 | 960 | **类型(Type)** | **电离式(Air Ionizer)**（对应负离子原理） |
| 15 | 1164 | 负离子浓度(Anion Density) | 可选最接近值 |
| 16 | 1222 | **使用环境(Usage Condition)** | **家用(Household)** |
| 17 | 1280 | 动力种类(Power Source) | （部分无选项） |
| 18 | 1396 | **覆盖面积(Coverage Area)** | **<10平方米(< 10 M²)** |
| 19-25 | 1454+ | 适用范围/类别/电源方式/风速/除苯率/除甲醛率等 | 按实际情况选；部分可能无可用选项 |

### ⚠️ 属性选项可能随时间变化（2026-06-11 验证）

AliExpress 的选项值会动态更新，不能完全依赖历史记录：
- **噪音(Noise)：** 历史上的「≤30分贝(≤30DB)」可能变为「≤35分贝(≤35dB)」。2026-06-11 实际可用选项中包含 ≤35分贝(≤35dB)，比 ≤30分贝 更接近 36dB以下。
- 每次操作时先检查实际可用的选项，再选最接近的。

## 1688 → AliExpress 属性值映射（2026-06-12 验证）

| 1688原始值 | AliExpress选项 | 验证日期 | 备注 |
|:--|:--|:--:|:--|
| 负离子工作原理 | 电离式(Air Ionizer) | 2026-06-07 | 类型(Type)列 |
| 36dB以下 | **≤35分贝(≤35dB)** | **2026-06-12** | 最接近的可用选项 |
| 50m³/h | 50立方米/小时(50m³/h) | 2026-06-12 | 完全匹配 ✓ |
| USB | USB(USB) | 2026-06-07 | 电源方式列 |
| —（无电压参数） | **DC5V(DC5V)** | **2026-06-12** | USB设备，选DC5V |
| —（无功率参数） | **1瓦(1w)** | **2026-06-12** | USB设备功率极小 |
| —（无HEPA） | **其他(Other)** | **2026-06-12** | 负离子款无滤网 |
| —（无高关注化学品） | **天然未处理(None)** | **2026-06-12** | 按用户要求选 |
| 按键式 | — | — | 无对应选项，描述中说明 |
| 滤网类型:无 | 其他(Other) | 2026-06-07 | HEPA列 |
| 白色,黑色,银色 | 需在SKU颜色区手动勾选 | 2026-06-07 | SKU变种 |

### ⚠️ 系统属性填写规则（2026-06-12 验证）

**共享Ant Design Select下拉面板问题：** 店小秘编辑页中所有系统属性下拉（品牌/电压/产地/风量/功率/HEPA/高关注/噪音）**共享同一个Portal下拉面板**。设置一个属性后再设置下一个，上一个的值可能被覆盖。建议分两轮设置。

**验证可自动设置的属性：**
- ✅ **品牌** → NONE(NONE) — 通过 `page.evaluate` label搜索 + `mouse.click` 坐标点击
- ✅ **产地** → 中国大陆 — 同上
- ✅ **风量** → 50立方米/小时 — 同上
- ✅ **噪音** → ≤35分贝(≤35dB) — 2026-06-12 可用
- ✅ **高关注化学品** → 天然未处理(None) — 2026-06-12 验证通过

**需要特殊处理的属性：**
- ⚠️ **电压** → DC5V(DC5V) — CDP模式下鼠标点击下拉后需搜索过滤再选，否则可能不保存
- ⚠️ **功率** → 1瓦(1w) — 同上
- ⚠️ **HEPA滤网等级** → 其他(Other) — 选项为 H13/H11/其他，选「其他」

**通用操作代码（已验证 2026-06-12）：**
```python
# 通过标签名找到下拉并鼠标坐标点击
coord = page.evaluate("""(labelText) => {
    var items = document.querySelectorAll('.ant-form-item');
    for (var i = 0; i < items.length; i++) {
        var label = items[i].querySelector('.ant-form-item-label label');
        if (label && label.textContent.includes(labelText)) {
            var sel = items[i].querySelector('.ant-select-selector');
            if (sel) {
                sel.scrollIntoView({block: 'center'});
                var r = sel.getBoundingClientRect();
                return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
            }
        }
    }
    return null;
}""", labelText)
page.mouse.click(coord['x'], coord['y'])
time.sleep(2)

# 从可见下拉选项中点击匹配项
page.evaluate("""(val) => {
    var opts = document.querySelectorAll('.ant-select-item-option');
    for (var opt of opts) {
        if (opt.offsetParent !== null) {
            var t = opt.textContent.trim();
            if (t.indexOf(val) !== -1) { opt.click(); return; }
        }
    }
}""", searchVal)
```

## 1688 包装数据提取参考

```
颜色 | 长(cm) | 宽(cm) | 高(cm) | 体积(cm³) | 重量(g)
白色 | 6     | 3     | 2     | 36       | 45
黑色 | 6     | 3     | 2     | 36       | 45
银色 | 6     | 3     | 2     | 36       | 45
```

单个产品重45g，AliExpress 上填0.080kg（含包装余量）

## 1688 功能亮点

- 负离子净化
- 50m³/h风量
- 36dB静音运行
- 高低压模式切换
- 按键智能操作
- USB便捷充电
- 多色可选
- 挂脖便携设计
- 供应商：温州市虹岳电器有限公司（自有工厂/跨境专供/OEM/ODM）

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*