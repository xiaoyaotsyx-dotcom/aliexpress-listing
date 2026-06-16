# 速卖通自动上架技能包 v3.0
# AliExpress Auto-Listing Skill Pack v3.0

[![License: AGPLv3](https://img.shields.io/badge/license-AGPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-latest-orange.svg)](https://playwright.dev/)

> AI驱动的自动化技能包——从1688采集到速卖通上架，通过店小秘全流程自动完成。
> An AI-powered automation toolkit that takes a 1688 product and publishes it to AliExpress via Dianxiaomi — end to end.

---

## 工作流总览
## Workflow Overview

> 流水线分5个阶段：启动 → 采集 → 编辑 → 审核 → 发布。
> The pipeline runs in 5 phases: Startup → Collection → Editing → QA → Publishing.

| 阶段 Phase | 内容 What happens | 自动化 Automated |
|:---|:---|:---:|
| 0 启动 Startup | Chrome CDP + Relay链 + 登录检查 / Chrome CDP + Relay chain + login check | ✅ |
| 1 采集 Collect | 1688搜索 → 采集到店小秘采集箱 / 1688 search → collect to Dianxiaomi inbox | ✅ |
| 2 编辑 Edit | 9个模块: 标题/分类/属性/图片/SKU/描述/包装/模板/其他 / 9 modules: title, category, attributes, images, SKU, description, packaging, templates, others | ✅ |
| 3 审核 QA | 扫描所有必填字段 → 确认9/9完成 / Scan all required fields → verify 9/9 complete | ✅ |
| 4 发布 Publish | 保存并移入待发布（需手动点一次按钮）/ Save and move to pending publish (one manual click required) | ⚠️ |

---

## 包含的技能 (15个)
## Skills Included (15)

> 15个模块化技能，适配 Hermes / Claude Code / Codex / 任何支持CDP的AI助手。
> 15 modular skills. Plug into Hermes, Claude Code, Codex, or any CDP-capable AI agent.

| # | 技能 Skill | 用途 Purpose | 阶段 |
|:---|:---|:---|:---:|
| 0 | dxm-startup | Chrome启动 + Relay + Playwright连接 / Chrome launch + Relay + Playwright connect | 启动 |
| 0.5 | dxm-collection | 1688产品采集 + 属性提取 / 1688 product collection + attribute extraction | 采集 |
| — | dxm-listing-workflow | 编排器：路由9个编辑模块 / Orchestrator: routes through all 9 edit modules | 编排 |
| 1 | dxm-basic-info | 英文标题 + 类目选择 / English title + category selection | 编辑 |
| 2 | dxm-dianxiaomi-info | 店小秘元数据（只读）/ Dianxiaomi metadata (read-only) | 编辑 |
| 3 | dxm-attributes | 9个必填属性 + 自定义属性清理 / 9 required attributes + custom attribute cleanup | 编辑 |
| 4 | dxm-product-images | 6张主图 / 裁800 / 翻译 / SKU图 / 6 main images, resize, translate, SKU images | 编辑 |
| 5 | dxm-sku-pricing | 定价公式 / 库存 / 物流 / SKU编码 / Pricing formula, inventory, logistics, SKU codes | 编辑 |
| 6 | dxm-pc-description | PC描述（模板+图片编辑+翻译）/ PC description (template + image editing + translation) | 编辑 |
| 7 | dxm-packaging | 包装重量和尺寸 / Package weight & dimensions | 编辑 |
| 8 | dxm-templates | 运费模板 + 服务模板 / Shipping template + service template | 编辑 |
| 9 | dxm-other-info | 海关 / EU合规 / 品牌制造商 / Customs, EU compliance, brand manufacturer | 编辑 |
| QA | dxm-qa-check | QA扫描 + 所有必填字段验证 / QA scan + verification of all required fields | 审核 |
| 主 | aliexpress-store-ops | 店铺运营主控（架构、铁律、避坑百科）/ Store ops master (architecture, rules, pitfalls) | 全局 |

---

## 定价公式
## Pricing Formula

```
零售价 = 货值 = (1688成本价 + ¥5) × 1.02 ÷ 0.413
Retail Price = Declared Value = (1688 Cost + ¥5) × 1.02 ÷ 0.413
```

> 公式涵盖国内运费(¥5)、2%退货率、30%平台费率、21%其他费率、20%净利率。
> Covers: domestic shipping (¥5), 2% return rate, 30% platform fees, 21% other fees, 20% net profit.

---

## 核心铁律
## Core Rules

1. **编辑页绝不刷新或重开。** 刷新即丢数据。
   **Never refresh or reload the edit page.** All data is lost on reload.

2. **断连后先 Target.getTargets 检查已有标签页。** 数据可能还在。
   **After disconnection, check Target.getTargets first.** Existing tabs may still hold your data.

3. **所有星号必填。** 9/9才算完成。
   **All starred fields must be filled.** 9/9 is the only passing grade.

4. **三振出局。** 同一操作3次失败→停手汇报。
   **Three strikes, you're out.** Same operation fails 3 times → stop and report.

5. **保存后通知用户手动点发布。** 最后一步对自动化免疫。
   **Save first, then manually click publish.** The final button resists all automation methods.

---

## 快速开始
## Quick Start

1. 启动Chrome调试模式 + CDP中继
   Start Chrome in debug mode with CDP relay

2. 打开店小秘手动登录（仅一次）
   Open Dianxiaomi and log in manually (once)

3. 对AI说："帮我上架产品"
   Tell your AI: "Help me list a product"

4. AI自动完成从采集到上架的全流程
   The AI handles the rest — from 1688 collection to publishing

5. 最后一步：在弹出的"保存并移入待发布"按钮上手动点击
   Final step: manually click the "Save and move to pending publish" button

---

## Requirements · 环境要求

- AI assistant with Python execution + CDP browser control · 支持 Python 执行 + CDP 浏览器操控的 AI 助手
- Google Chrome (your own login) · Chrome 浏览器（你自己的登录态）
- Dianxiaomi ERP account · 店小秘 ERP 账号
- Chrome launched in debug mode: `--remote-debugging-port=9222`

---

## License · 许可

**AGPLv3 Dual License · 双许可**

| Use Case · 使用场景 | License · 许可 |
|------|---------|
| Personal, non-commercial · 个人非商业 | AGPLv3 ✅ Free · 免费 |
| Company ≤5 seats · 企业≤5人 | AGPLv3 ✅ Free · 免费 |
| Company 6+ seats / Commercial · 企业6+人/商用 | [Contact us · 联系我们](mailto:Walter.x@qq.com) |

---

## ⚠️ 重要提示
## Important Note

> **最后一步"保存并移入待发布"按钮对目前已知的所有自动化方法免疫。** 这不是技能包的bug，是店小秘平台的反自动化机制。用户在收到QA扫描完成通知后，需手动点击一次该按钮即可完成上架。
> **The final "Save and move to pending publish" button resists all known automation methods.** This is Dianxiaomi's anti-automation mechanism, not a bug. After receiving the QA scan completion notification, the user only needs one manual click to finish.

---

## Contact · 联系

- 📕 RedNote · 小红书: [@瑞吉AI人民公社](https://www.xiaohongshu.com/user/profile/42084313799)
- 📧 Walter.x@qq.com

---

*Rigi AI Commons — Reject AI echo chambers. Democratize practical AI for everyone.*
*Rigi AI Commons — 拒绝 AI 小圈子自嗨，推动实用 AI 全面普惠。*
