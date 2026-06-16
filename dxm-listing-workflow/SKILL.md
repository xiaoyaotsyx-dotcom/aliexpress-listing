---
name: dxm-listing-workflow
description: 店小秘速卖通上品完整工作流——从采集箱到发布的所有模块编排、调用顺序、区域调价、保存发布
domain: ecommerce
triggers:
  - 用户说"上品"、"发布"、"继续上架"、"重新跑一遍"、"完整工作流"
  - 用户需要在店小秘完成从采集到发布的全流程
---

# 店小秘速卖通上品完整工作流

> 最后验证：2026-07-19 | 验证产品：折叠喝水神器

## 全流程（5阶段）

```
阶段0: 启动 → dxm-startup | Chrome CDP + Relay + Playwright连接
阶段1: 采集 → dxm-collection | 1688搜索 → 采集到店小秘采集箱
阶段2: 编辑 → dxm-listing-workflow | 采集箱 → 编辑页 → 9模块填表
阶段3: 审核 → dxm-qa-check | QA扫描所有星号字段
阶段4: 发布 → 保存并移入待发布 | 通知用户手动点击
```

## 架构

```
店小秘编辑页（单页面 + anchor滚动导航）
  ├── 0. 启动与登录 (dxm-startup)
  ├── 0.5 1688采集 (dxm-collection)
  ├── 1. 基本信息 (#basicInfo)
  ├── 2. 店小秘信息（只读）
  ├── 3. 属性信息 (#attrInfo)
  ├── 4. 产品信息 (#productProductInfo)
  ├── 5. 区域调价（跳过）
  ├── 6. 描述信息 (#descriptionInfo)
  ├── 7. 包装信息 (#packageInfo)
  ├── 8. 模板信息 (#templateInfo)
  └── 9. 其他信息 (#otherInfo)
```

## 🔴 铁律（最高优先级）

1. **编辑页绝不刷新/重开** — 上架操作期间禁止 browser_navigate
2. **断连后先检查已有标签页** — Target.getTargets → 找到编辑页 → 验证状态 → 关闭空白页 → 激活正确页
3. **所有星号必填** — 少1个都不算完成
4. **有下拉的都选值** — 非星号下拉也要选（除非免疫）
5. **不做无意义的3次以上重试** — 3次失败停手汇报
6. **不要问用户下一步做什么** — skill里全有
7. **不要问用户自己操作** — 能填的全填

## 完整流程（9步）

### Step 1: 基本信息 → `dxm-basic-info`

- 标题纯英文，128字符内
- 分类：点「选择分类」→ 四列树弹窗 → 按标题关键词匹配叶子节点 → 点「选择」确认
- 分类选错会导致SKU属性「已废弃」→ 改分类自动修复

### Step 2: 店小秘信息 → 跳过（只读）

- 来源URL已自动填入，不修改

### Step 3: 属性信息 → `dxm-attributes`

**前置：先开1688新标签页提取参数**

星号字段枚举（必须9/9）：
| 字段 | 来源 | 常用值 |
|------|------|--------|
| 产地 | 固定 | 中国大陆 |
| 品牌 | 固定 | NONE |
| 液晶显示 | 推断 | 无(No) |
| 最大出餐量 | 推断 | 500g（根据产品） |
| 最小出餐量 | 推断 | 100g |
| 材质 | 1688 | 硅胶→Plastic |
| 是否智能 | 推断 | no |
| 高关注化学品 | 固定 | 天然未处理 |
| 是否包含电池 | 推断 | no |

**操作方式：JS强制显示dropdown + click**（首选），Playwright mouse.click坐标法（备选）。

⚠️ 非星号字段（电源/电压/类型/动力）如遇免疫，跳过不纠缠。

操作完删自定义属性。

### Step 4: 产品图片 → `dxm-product-images`

- 主图选6张（白底多角度优先）
- 批量改尺寸800×800
- 图片翻译：页顶「一键翻译」按钮，点两次（选语言→提交）
- 营销图片一键生成
- 颜色SKU改名（用「批量编辑」弹窗）
- SKU图改尺寸+翻译
- 容量：350ml（根据产品推断）

### Step 5: SKU定价 → `dxm-sku-pricing`

| 字段 | 值 | 来源 |
|------|-----|------|
| 零售价 | 公式计算 | =货值 |
| 货值 | 公式计算 | =零售价 |
| 库存 | ≤2000 | 1688原始数据 |
| 重量 | 0.2kg | 1688 (200g÷1000) |
| 是否原箱 | 是(1) | 固定 |
| 物流属性 | 普货 | 无电产品 |
| 商品编码 | 一键生成 | 自动 |

**定价公式：** `零售价 = (1688成本价 + ¥5) × 1.02 ÷ 0.413`（净利率20%）

⚠️ SKU表每placeholder有3个匹配：nth(0)=SKU1, nth(2)=SKU2, nth(1)=隐藏行跳过

### Step 6: PC端描述 → `dxm-pc-description`

- 引用模板
- 批量改图片尺寸：JS强制显示 `.images-options` → 固定到视口 → 点击下拉 → 选批量改尺寸 → 填800 → 生成JPG
- 图片翻译：同入口 → 图片翻译 → 一键翻译点两次

### Step 7: 包装信息 → `dxm-packaging`

- 包装后重量：0.2kg（1688提取）
- 包装后尺寸：1688无数据跳过

### Step 8: 模板信息 → `dxm-templates`

- 运费模板：根据零售价选对应档位
- 服务模板：Service Template for New Sellers
- 海关监管属性：默认3，不修改

### Step 9: 其他信息 → `dxm-other-info`

| 字段 | 操作 | 方法 |
|------|------|------|
| 半托管服务 | 跳过不碰 | — |
| 报价是否含关税 ⭐ | 点「不含关税报价」 | JS click radio |
| 欧盟责任人 | 选唯一选项 | JS click → select option |
| 品牌制造商 | 选唯一选项 | **keyboard Enter**（JS click无效！） |
| 土耳其责任人/商机品/资质 | 跳过 | — |

### 收尾：保存并移入待发布

所有模块填完 → QA检查通过 → 点「保存」→ **通知用户手动点「保存并移入待发布」**

⚠️ **「保存并移入待发布」按钮对所有automation免疫（已验证：CDP mouse、Playwright mouse、JS click、dispatchEvent、keyboard Enter全无效）。** 自动化只能做到「保存」按钮。用户需手动完成最后一步。

## QA检查清单

- [ ] 标题纯英文无中文字符错误
- [ ] 分类已选（非「请选择」）
- [ ] 所有星号属性 9/9 已填
- [ ] 主图6张已选
- [ ] 图片已改尺寸800×800
- [ ] SKU定价公式正确（零售价=货值）
- [ ] 库存、重量已填
- [ ] 物流属性已选
- [ ] 商品编码已生成
- [ ] PC描述有内容（非空）
- [ ] 包装后重量已填
- [ ] 运费/服务模板已选
- [ ] 报价不含关税已点
- [ ] 欧盟责任人已选
- [ ] 品牌制造商已选
- [ ] **品牌仍为NONE（填完制造商后验证！）**

## 已知全局坑点

1. **🔴 browser_navigate会刷新已有标签页，导致所有未保存数据丢失** → 连接中断后绝对不要用browser_navigate切回编辑页！用Target.activateTarget或Playwright page.bring_to_front()
2. **browser_snapshot截断** → 用 execute_code + websocket CDP全页扫描替代
3. **品牌制造商免疫JS click** → 用 keyboard.press('Enter')
4. **品牌制造商填完后必须验证品牌仍为NONE** → keyboard Enter可能误触品牌字段（高频——已验证至少3次）。Save前必须读回品牌值确认。
5. **电源/电压/动力免疫所有automation** → 跳过不纠缠
6. **ant-modal-wrap拦截** → 部分弹窗按钮用JS element.click()兜底
7. **一键翻译点两次** → 第1次选语言，第2次提交
8. **不要依赖「保存」按钮存草稿** → 一次性填完再保存
9. **🔴 店小秘公告弹窗拦截（2026-07-19）：** 登录后可能弹出全屏公告弹窗（618促销等），拦截所有Playwright locator.click()。**开始编辑前必须先用JS清除：** `document.querySelectorAll('.ant-modal-wrap, .notice-list-modal, .bullet-layer').forEach(m => m.remove())`
10. **🔴 属性下拉共享池乱串（2026-07-19）：** 多个ant-select的dropdown在DOM中共存时，`querySelectorAll('.ant-select-dropdown')` 可能返回错误dropdown。必须**逐字段操作、每次关闭所有dropdown、用`dds[dds.length-1]`取最新**。但即使如此仍有概率失败。属性字段是自动化最脆弱的环节，如连续失败不要死磕——先填其他模块。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*