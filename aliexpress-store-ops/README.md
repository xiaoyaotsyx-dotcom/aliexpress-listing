# AliExpress Listing Automation — AI-Powered Product Publishing

**Turn hours of manual data entry into minutes of automated work.**

AliExpress Listing Automation is a complete AI agent workflow that automates the entire cross-border e-commerce product listing pipeline — from sourcing product data on 1688, to filling attributes, pricing, images, and descriptions inside Dianxiaomi ERP, all the way to saving drafts ready for publishing. It's a set of battle-tested Skills and scripts that your AI assistant loads and executes step by step, just like a human operator would.

---

# 速卖通AI上架——智能体驱动的产品发布工作流

**把几小时的手动填表变成几分钟的全自动操作。**

这是一个完整的 AI Agent 工作流，覆盖跨境卖家从1688采集产品数据、到在店小秘ERP中自动填写属性/定价/图片/描述、再到保存移入待发布的全流程。底层是经过实战验证的 Skill 和脚本，AI 助手加载后即可像真人操作员一样逐步完成上架。

---

## What Problem Does This Solve?

Cross-border sellers spend 40–60 minutes per product manually copying data from 1688 into Dianxiaomi: translating titles, selecting categories, filling 50+ attribute fields, resizing images, setting SKU pricing and logistics. With 10 products a day, that's an entire workday wasted on data entry.

This workflow automates everything that CAN be automated, and clearly documents what CANNOT — so you only need to click one or two buttons manually.

---

## 解决什么问题？

跨境卖家每上一个产品，要在店小秘里手动填50+字段：翻译标题、选类目、填属性、改图片尺寸、设SKU价格和物流。一个品40-60分钟，一天10个品就是整整一个工作日。

本工作流把能自动化的全部自动化，不能自动化的坑点全部标注清楚——你只需要手动点一两下。

---

## How It Works — The Technology

The workflow uses **Chrome CDP (Chrome DevTools Protocol)** to control your REAL browser — not a simulated headless browser. Your AI assistant connects to the Chrome window where you're already logged into Dianxiaomi and 1688. It clicks, types, selects dropdowns, and fills forms using the same browser session. The websites see a real human operating — because it IS your real browser.

Under the hood: Playwright automation + CDP mouse event injection + Vue 3 DOM manipulation — all battle-tested against Dianxiaomi's notoriously difficult ant-design component library.

---

## 技术原理

工作流的底层是**Chrome CDP（Chrome开发者工具协议）**——不模拟浏览器，而是直接操控你已经打开的真实 Chrome 窗口。AI 助手连接到你已登录店小秘和1688的浏览器页面，在同一个会话里点击、打字、选下拉框、填表。网站看到的是一个真人在操作，因为操作的的确是你真实的浏览器。底层技术栈：Playwright 自动化 + CDP 鼠标事件注入 + Vue 3 DOM 操作，全部在店小秘那个出了名难搞的 ant-design 组件库上实打实验证过。

---

## What It Can Do — Complete Pipeline

| Step | Action | Status |
|------|--------|:------:|
| 0 | Enter Dianxiaomi collection box | ✅ |
| 1 | Open product editor | ✅ |
| 2 | Translate title to English | ✅ |
| 3 | Select product category | ✅ |
| 4 | Extract parameters from 1688 | ✅ |
| 5 | Fill product attributes | ✅ |
| 6 | Remove custom attributes | ✅ |
| 7 | Select + resize + translate product images | ✅ |
| 8 | Fill SKU pricing (retail/cost/inventory/weight/logistics) | ✅ |
| 8.5 | PC description (template + image resize + translation) | ✅ |
| 9 | Save and move to pending publish | ✅ |

---

## 完整流程

| 步骤 | 操作 | 状态 |
|------|------|:----:|
| 0 | 进入店小秘采集箱 | ✅ |
| 1 | 打开编辑页 | ✅ |
| 2 | 标题中译英 | ✅ |
| 3 | 选择产品分类 | ✅ |
| 4 | 从1688提取产品参数 | ✅ |
| 5 | 填写产品属性 | ✅ |
| 6 | 删除自定义属性 | ✅ |
| 7 | 选图+批量改尺寸+图片翻译 | ✅ |
| 8 | SKU定价(零售价/货值/库存/重量/物流) | ✅ |
| 8.5 | PC端描述(模板+改尺寸+图片翻译) | ✅ |
| 9 | 保存并移入待发布 | ✅ |

**Full pipeline verified 2026-07-19.** One product, Step 0 to Step 9, all required fields filled. Everything automatable is automated. Everything that resists automation is documented as a known pitfall.

---

## Supported AI Platforms

| Platform | Support |
|----------|:-------:|
| Hermes Agent | ✅ |
| Claude Code | ✅ |
| OpenAI Codex | ✅ |
| Cursor | ✅ |
| Open Interpreter | ✅ |

Any AI assistant capable of executing Python scripts, reading local files, and controlling a browser via CDP is compatible.

---

## 支持的AI平台

| 平台 | 支持 |
|------|:----:|
| Hermes Agent | ✅ |
| Claude Code | ✅ |
| OpenAI Codex | ✅ |
| Cursor | ✅ |
| Open Interpreter | ✅ |

凡是能执行Python脚本、读取本地文件、通过CDP操控浏览器的AI助手都可以使用本工作流。

---

## Quick Start (3 minutes)

1. Download this folder to your AI assistant's skills directory
2. Say: *"Load AliExpress listing workflow"*
3. Open Dianxiaomi and 1688 in Chrome (remote debugging enabled)
4. Say: *"Help me list this product"* — follow the AI's guidance

---

## 快速开始（3分钟）

1. 下载本文件夹到 AI 助手的 skills 目录
2. 对AI说：*"加载速卖通上架工作流"*
3. 在Chrome中打开店小秘和1688（需开启远程调试模式）
4. 对AI说：*"帮我上架这个产品"*，跟着AI引导走

---

## Known Limitations & Call for Contributors

- Some non-required dropdown fields resist all known automation — documented as known pitfalls
- The final "Save and move to pending publish" button requires a manual click
- Dianxiaomi's full-screen announcement popups are auto-detected and cleared

**PRs welcome.** If you crack one of these, the entire cross-border seller community benefits.

---

## 已知局限 & 共建邀请

- 部分非必填下拉字段对所有自动化方法免疫——已标记为已知坑点
- 「保存并移入待发布」按钮需手动点击一次
- 店小秘不定时全屏弹窗——工作流已内置自动检测关闭

**欢迎PR。** 攻克任何一个坑点，受益的是整个跨境卖家群体。

---

## ⚠️ Disclaimer

This workflow automates browser operations on your behalf. It clicks, types, and fills forms in your real browser. **Use at your own risk.** The authors are not responsible for any account issues, data loss, or policy violations.

**本工作流代替你在浏览器中操作：点击、打字、填表。使用风险自负。作者不对任何账号问题、数据丢失或违规行为负责。**

---

## Author

**Rigi AI Commons**

📕 Xiaohongshu: **@瑞吉AI人民公社**

*拒绝 AI 小圈子自嗨，推动 AI 全面普惠。每一个普通人，都应有平等使用和创造 AI 工具的权利。*

*Rejecting AI echo chambers. Democratizing AI for everyone. Every ordinary person deserves the right to use and create with AI.*

---

*Author: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*
