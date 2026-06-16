---
name: dxm-basic-info
description: 店小秘速卖通编辑页——基本信息模块：标题改英文 + 产品分类选择
domain: ecommerce
triggers:
  - 用户说"改标题"、"标题英文"、"基本信息"、"选分类"
  - 店小秘编辑页打开后需要填基本信息
---

# 店小秘基本信息模块

## 环境

CDP browser_cdp 直连：
- `GET /json/version` → 获取 webSocketDebuggerUrl
- `Target.getTargets` → 找编辑页 target
- `Runtime.evaluate` + `Page.navigate` + `Input.dispatchMouseEvent`

编辑页 URL 格式：`https://www.dianxiaomi.com/web/smt/edit?id={product_id}`

## Step 1：标题改为英文

### 规则
- 纯英文，128字符以内
- 从1688中文标题翻译，保留核心关键词
- 示例：`折叠喝水神器随行杯便携式饮水器狗狗外出饮水杯` → `Collapsible Portable Dog Water Bottle Travel Pet Water Dispenser Outdoor Drinking Bowl`

### CDP 操作
```
Runtime.evaluate:
  const input = document.querySelector('input[placeholder*="标题"], textarea[placeholder*="标题"]');
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  setter.call(input, 'ENGLISH TITLE HERE');
  input.dispatchEvent(new Event('input', {bubbles: true}));
  input.dispatchEvent(new Event('change', {bubbles: true}));
```

### ⚠️ 注意
- 必须用 nativeInputValueSetter，Vue 3 不响应直接 `el.value = xxx`
- 填完后用 `Runtime.evaluate` 读回验证

## Step 2：选择产品分类

### 页面位置
**基本信息 tab** → 「产品分类」字段旁边的「选择分类」按钮（注意：分类在基本信息 tab，不是属性信息 tab）

### 弹窗结构（2026-06-14 实战验证）

分类弹窗使用 `.categories-box` 结构，**不是 ant-tree**：
- 4 个 `.categories-box`，每个代表一层树
- 每列内 `.categories-item` 是可点击节点
- 当前选中节点带 `class="active"`
- 面包屑路径：`家居用品(Home & Garden) > 宠物用品(Pet Products) > 养狗用品(Dog Supplies) > 狗携带用品(Dog Carriers & Bags)`

### CDP 操作流程（已验证有效）

**选择逻辑：**
1. 找到「选择分类」按钮（基本信息 tab，坐标约 x=1017, y=405）
2. `Input.dispatchMouseEvent mousePressed + mouseReleased` 打开弹窗
3. 等 1-2 秒让弹窗渲染
4. 按面包屑路径逐列定位：列0→一级、列1→二级、列2→三级、列3→叶子
5. 在目标列中找 `.categories-item-name` textContent 匹配 → 点击
6. 验证该 item 变为 `class="active"`
7. 点弹窗 footer 的「选择」按钮确认（坐标约 x=1539, y=579）

### 分类命名规则
- **优先按标题关键词找完全匹配类目**
- 无完全匹配时选最接近的
- 宠物用品常见类目：`宠物用品 > 狗 > 携带用品 > 狗携带用品`

### ⚠️ 已知坑点
1. 分类弹窗用 `.categories-box` 不是 ant-tree，不要用 hover 展开——直接点击 `.categories-item-name`
2. 弹窗内列的内容可能很长需要滚动
3. 分类选错会导致 SKU 属性全部「已废弃」——改分类后自动修复
4. 用 CDP `Input.dispatchMouseEvent`，不要用 JS `.click()`（Vue 3 不响应）
5. 分类在**基本信息 tab**，不在属性信息 tab

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*