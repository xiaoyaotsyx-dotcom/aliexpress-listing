# 1688 → 店小秘 属性映射参考

## 挂脖空气净化器 / 迷你风扇类

从1688属性表提取参数后，在店小秘属性信息tab中选最接近的值。

### 核心属性映射

| 1688参数 | 1688值示例 | 店小秘选项（选最接近） | 说明 |
|:--|:--|:--|:--|
| 品牌 | 其它 | NONE(NONE) | 无品牌产品一律选NONE |
| 工作原理 | 负离子 | 看功能(Function)中有无相关选项 | 负离子在1688是工作原理，店小秘可能在功能中 |
| 噪音 | 36dB以下 | ≤35分贝(≤35dB) 或 ≤30分贝(≤30DB) | 2026-06-11 验证：AliExpress 实际选项可能有 ≤35分贝(≤35dB)。日常操作时先检查当日可用选项，选最接近的。如果两者都有，≤35分贝 更接近 36dB。 |
| 适用面积 | 10㎡及以下 | <10平方米(< 10 M²) | 精确匹配 |
| 颜色 | 白色、黑色、银色 | 对应AliExpress颜色值 | 自定义名称填英文（White/Black/Silver）|
| 款式 | 挂脖 | 对应安装方式(Installation)或类型(Type) | 看哪个属性有相关选项 |
| 适用场景 | 家用 | 家用(Household) | 精确匹配 |
| 安装方式 | 不需安装 | 便携式(Portable)或迷你型(Mini) | 选"不需要安装"相关 |
| 电源方式 | USB | USB(USB) | 精确匹配 |
| 插头规格 | 其他规格 | 其他(Other)或不填 | 非必填 |
| 风量 | 50立方米/小时 | 50立方米/小时(50m³/h) | 精确匹配 |
| 控制方式 | 按键式 | 选对应选项 | 如果有按键式选项就选，没有就选最近似 |
| HEPA滤网等级 | 无/不适用 | 其他(Other) | **1688没有HEPA滤网的产品绝不选H13/H11等**！选"其他(Other)"。用户明确纠正：「滤网等级，你没有看到旁边滤网类型是无吗？那你就要选其他」 |
| 高关注化学品 | 无 | 天然未处理(None) | 多选字段。先清掉其他所有化学品（toggle off），只保留天然未处理。操作方式见 `multi-select-toggle.md` |

### 属性值不匹配的处理

1688的中文值可能没有精确对应的AliExpress选项：

1. **数值范围不匹配**（如36dB以下 → 选项有≤30/≤50/≤55）
   - 选最接近且**不劣于**1688的选项
   - 例：36dB以下 → ≤30分贝（比36更安静，ok）
   - 例：不选≤50分贝（比36噪音大，会显得产品更吵）

2. **表述方式不匹配**（如"不需安装" → 选项有"迷你型"/"便携式"/"USB接口型"）
   - 选含义最接近的：不需安装 → 便携式(Portable)
   - 不要选"迷你型"（这是尺寸描述不是安装方式）
   - 不要选"USB接口型"（这是电源方式不是安装方式）

3. **1688有但店小秘没有对应属性**
   - 跳过，不用填（除非带红色星号）
   - 在产品描述中补充说明

### 属性填写验证

填完所有属性后，必须检查：
1. 所有带红色星号的属性都已填写（非空值）
2. 1688有对应数据的属性已按最接近值填写
3. 没有多余的自定义属性残留

### 常见错误（此会话中被用户纠正）

| 错误做法 | 正确做法 |
|:--|:--|
| 选第一个可用选项 | 对照1688参数表，选最接近的值 |
| 噪音选≤50分贝 | 1688写36dB以下，应选≤30分贝 |
| 使用环境选"车充" | 1688写"家用"，应选"家用(Household)" |
| 电源方式选"交流电" | 1688写"USB"，应选USB |
| 安装方式选"迷你型" | 1688写"不需安装"，应选"便携式(Portable)" |
| 功能选"除臭" | 1688写"负离子"，应选"杀菌/净化"相关 |

### 提取1688参数的标准化流程

```python
# 1. 点击展开全部参数
page.evaluate("""() => {
    var all = document.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
        if (all[i].textContent && all[i].textContent.indexOf('全部参数') != -1) {
            all[i].click(); return;
        }
    }
}""")
time.sleep(2)

# 2. 提取表格行
params = page.evaluate("""() => {
    var rows = document.querySelectorAll('table tr');
    var results = [];
    for (var i = 0; i < rows.length; i++) {
        var cells = rows[i].querySelectorAll('td');
        if (cells.length >= 2)
            results.push(cells[0].textContent.trim() + ': ' + cells[1].textContent.trim());
    }
    // 表格方案失败时回退到文本提取
    if (results.length === 0) {
        var text = document.body.innerText || '';
        var s = text.indexOf('品牌');
        var e = text.indexOf('供应商信息');
        return text.substring(s, e > s ? e : s + 2000).split('\\n').filter(Boolean);
    }
    return results;
}""")

# 3. 搜索关键参数
for kw in ['品牌', '噪音', '电源', 'USB', '功率', '电压', '风量', '颜色', '重量', '尺寸', '功能', '适用', '安装', '插头', '控制']:
    for p in params:
        if kw in p: print(p)
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*