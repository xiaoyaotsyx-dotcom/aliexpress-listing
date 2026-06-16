# 分类变更导致的 SKU 和属性修复（2026-07-12 记录）

## 场景
产品在「狗自动喂食/喂水器」分类下，SKU 颜色/尺寸全部显示「该属性值平台已废弃，不支持选择！」
改到「狗携带用品」后页面重新渲染，出现了新字段。

## 操作记录

### 1. 分类选择弹窗（antd modal）
- 树形导航 hover 展开子级（`mouseMoved`），click 选中叶子节点
- 底部「选择」按钮需要在 scroll modal-wrap 后才能点击
- 确认后分类路径更新到面包屑，但关闭后顶部黄色警告仍显示

### 2. 分类变更后的字段变化

| 旧字段（消失） | 新字段（出现） |
|:--|:--|
| 液晶显示(LCD Display)* | 中国省份(CN)* |
| 最大出餐量(Max Output)* | 产品类型(Item Type)* |
| 最小出餐量(Min Output)* | 品种大小(Breed size)* |
| 是否智能(Is Smart Device)* | 高关注化学品(High-concerned chemical)* |
| 电压(Voltage) | 类型(Type) |
| 动力来源(Power Source) | 图案类型(Pattern Type) |

### 3. SKU 变种变化
旧分类下颜色有 15+ 种选项（白/黑/绿/红/灰/蓝/黄/粉/紫...），全部显示已废弃。
新分类后 SKU 变种会自动调整为 白色/黑色（2个颜色选项），自定义名称保留中文但会报错。

### 4. 已验证的值映射

**高关注化学品（[7] rc_select_22）：**
下拉包含大量化学品列表，第一项「天然未处理(None)」是唯一合适的选项。
必须通过 CDP click打开 → 读取可见选项 → 点击匹配项。

**品种大小（[8] rc_select_33）：**
选项包含「小包装(Small Breeds)」（实际是犬种大小，选项仅 小包装 一种匹配项）。

**产品类型（[5]）：**
选项包含：双肩背包、汽车携带用品、自行车携带用品、软面携带包、手推车、斜跨式包
为给旅行水壶选最接近的 →「汽车携带用品(Car Travel Accessories)」

### 5. 填写顺序（已验证有效）
1. 关闭所有下拉（点击 (5,5) 空白处）
2. scrollIntoView({block: 'center'}) 确保元素在视口
3. CDP mouse.click 打开下拉
4. 读取所有 `.ant-select-dropdown` 中的可见 `.ant-select-item-option` 元素
5. 按文本匹配目标选项 → CDP mouse.click 选中
6. 不需要额外确认，antd 自动关闭下拉

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*