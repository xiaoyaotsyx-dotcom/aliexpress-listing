---
name: aliexpress-store-ops
description: 速卖通店铺运营自动化 — 每日巡检/每周策略/商品上架/数据分析全流程。填入你的店铺名即可使用。
domain: ecommerce
version: "1.0.0"
modelVersion: "1.0.0"
lastUpdated: "2026-07-19"
compatibility: "Hermes Agent ≥ v1.0 | Claude Code ≥ v2.0 | Codex ≥ v1.0"
authors:
  - "Rigi AI Commons (小红书 @瑞吉AI人民公社)"
license: "MIT"
lifecycle: "active"
triggers:
  - 用户说"帮我看看店铺"、"分析数据"、"上品"、"发新品"、"做策略"
  - 用户需要定时查看店铺运营状态
  - 用户需要数据驱动的产品营销策略
  - 用户说"帮我在店小秘上架"、"采集1688"、"参考产品上架"
  - 用户打开1688页面和店小秘编辑页，需要帮忙填写产品信息
  - 用户说"先学习这个再填那个"、"照这个产品填"（参考产品法）
  - 用户打开多个浏览器标签页需要Agent在标签页间操作学习
---
# 速卖通运营工作流（填入你的店铺名即可使用）

## 🔴 铁律第一：上架操作期间禁止刷新/重载页面

**这是最高优先级规则，违反会导致数据全丢，必须重新操作。**

进入编辑页（`smt/edit?id=...`）后，在全部操作完成（保存并移入待发布）之前：
- ❌ **禁止**调用 `browser_navigate` 刷新页面
- ❌ **禁止**调用 `page.goto()` 重载编辑页
- ❌ **禁止**在编辑页和采集箱列表之间来回跳转
- ❌ **禁止**手动刷新浏览器标签页
- ❌ **禁止**关闭编辑页再重新打开

**唯一允许刷新的场景：** 页面死机/卡住/完全无法操作。

**正确的数据查看方式：** 用 `page.evaluate()` 在页面内读取 DOM 值，不要刷新页面。

**正确的数据保存方式：** 全部填完后一次性点「保存并移入待发布」。不要依赖「保存」按钮存草稿。

**如果必须查其他页面的数据（如 1688 参数）：**
1. 在**新标签页**中打开（`ctx.new_page()` 或浏览器新标签）
2. **店小秘编辑页「来源URL → 访问」按钮也必须开新标签页** —— 绝对不能让该页面覆盖编辑页
3. 查完切回编辑页继续操作
4. 同一个编辑页的 Playwright 会话不中断

## 架构（永久 CDP 中继）

```
Windows Chrome (--remote-debugging-port=9222)
  ↕ Relay2.exe (0.0.0.0:9255 → 127.0.0.1:9222)
  ↕ 开机 VBS 自启 (Startup/hermes-chrome-relay.vbs)
Windows IP (172.24.48.x:9255)
  ↕ WSL chrome_relay.py (localhost:19223 → GW:9255)
```

## ⚠️ CDP 中继故障处理
详见 `references/cdp-recovery.md`

### 🚨 Gateway断连后重连铁律（2026-07-19新增）

**致命错误：** gateway重启/断连后，直接调用 `browser_navigate` 会**创建新标签页**，而不是连回已有的填好数据的标签页。这会导致之前所有未保存的填写工作"消失"（实际在另一个标签页中）。

**正确恢复步骤：**
```
1. browser_cdp → Target.getTargets     # 列出所有标签页
2. 从返回的 targetInfos 中找到店小秘编辑页（title="店小秘--编辑速卖通产品"）
3. 对每个编辑页 target: Runtime.evaluate 读取页面状态（标题、hash、bodyText片段）
4. 确认哪个标签页有已填数据（英文标题、已选属性值等）
5. 关闭空白/重复标签页: Target.closeTarget
6. 激活正确的标签页: Target.activateTarget
7. 此时 browser_snapshot 应该显示已填数据
```

**禁止操作：**
- ❌ 断连后直接 browser_navigate → 创建重复空白页 → 数据"丢失"
- ❌ 不检查 Target.getTargets 就操作
- ❌ 在已有填好数据的情况下重新填写（浪费时间）

## 模块化 Skill 体系（2026-07-19 全流程验证通过）\n\n店小秘编辑页拆分为独立模块，每个模块有对应 Skill。\n\n| 模块 | Skill | 状态 | 验证日期 |\n|------|-------|------|----------|\n| 1. 基本信息 | `dxm-basic-info` | ✅ | 07-19 |\n| 2. 店小秘信息 | 只读，跳过 | — | — |\n| 3. 属性信息 | `dxm-attributes` | ✅ | 07-19 |\n| 4. 产品图片 | `dxm-product-images` | ✅ | 07-19 |\n| 5. SKU定价 | `dxm-sku-pricing` | ✅ | 07-19 |\n| 6. PC端描述 | `dxm-pc-description` | ✅ | 07-19 |\n| 7. 包装 | `dxm-packaging` | ✅ | 07-19 |\n| 8. 模板 | `dxm-templates` | ✅ | 07-19 |\n| 9. 其他信息 | `dxm-other-info` | ✅ | 07-19 |\n| 总调度 | `dxm-listing-workflow` | ✅ 完整 | 07-19 |\n\n> **2026-07-19 全流程验证：** 产品\"折叠喝水神器\"从 Step 0 到 Step 9 全部走通。所有星号必填项已填。剩余已知问题：3个非星号下拉（电源/电压/动力）对所有automation免疫 → 跳过不纠缠（已记录 pitfall #14）。"\n\n## 上架流水线 — 分步操作流程

### 流程总览（15步）

```
Step 0 → 进入采集箱
Step 1 → 点「编辑」进编辑页
Step 2 → 标题改为英文
Step 3 → 选分类（弹窗树）
Step 4 → 开1688查参数（新标签页）
Step 5 → 填产品属性（红色星号必填）
Step 6 → 删除自定义属性
Step 7 → 产品图片选图
Step 7.5 → 批量改尺寸800×800
Step 7.6 → 图片翻译中文→英文
Step 7.7 → 营销图片一键生成
Step 7.8 → 颜色SKU：改英文名+图改尺寸+图翻译
Step 8  → SKU定价栏
Step 8.5 → PC端描述（引用模板 + 批量改图片尺寸）
Step 9  → 保存并移入待发布
```

详细操作指南（含代码片段、坐标、验证方法、已知坑点）全部放入以下参考文件：

### 参考文件清单

| 文件 | 内容 | 来源步骤 |
|:--|:--|:--|
| `references/cdp-recovery.md` | CDP 中继重启/故障恢复 | 架构 |
| `references/sku-table-fields.md` | SKU表HTML结构、select索引、颜色配置、字段映射 | Step 8 |
| `references/sku-variant-config.md` | VXE Table 结构、批量行vs单行、颜色配置 | Step 8 |
| `references/step-by-step-mode.md` | 步进模式、三击全选、交互规则 | 通用 |
| `references/batch-listing-workflow.md` | 30品/天上架流水线作业手册 | 通用 |
| `references/publishing-checklist.md` | 发布前检查清单 | Step 9 |
| `references/pc-description-template.md` | PC端描述所有操作：引用模板 + 批量改图片尺寸 + 图片翻译 | Step 8.5 |
| `scripts/detect-chinese-text.py` | OCR检测图片中是否含中文文案，配合图片翻译使用 | Step 8.5 |
| `references/attribute-fill-cdp.md` | 属性批量填写：CDP坐标两步法 + 狗携带用品属性值速查 | Step 5 |
| `references/playwright-coordinate-click.md` | Playwright mouse.click(x,y) 坐标法填 ant-select（比CDP更可靠触发Vue3） | Step 5 |
| `references/1688-json-extraction.md` | 1688嵌入JSON正则提取法 | Step 4 |
| `references/cdp-direct-operation.md` | browser_cdp 直连模式：弹窗拦截绕过 + 鼠标事件 + 截图 | 通用 |
| `references/sku-code-patterns.md` | SKU配置代码模式速查 | Step 8 |

### 各步骤核心规则速查

#### Step 0-1：进入采集箱 → 编辑页
- 左侧菜单「产品→采集箱→速卖通采集箱(N个)」
- 点击操作列「编辑」在新标签页打开编辑页
- URL格式：`https://www.dianxiaomi.com/web/smt/edit?id={product_id}`
- 进入编辑页后立即检查：标题是否含中文？分类是否有警告？必填属性是否为空？

#### Step 2：标题 → 英文
- 纯英文，128字符以内
- 使用 `nativeInputValueSetter` 操作

#### Step 3：选择分类
- 点击「选择分类」按钮 → 弹出4框树弹窗
- 按标题关键词找完全匹配类目，没有则选最接近
- 点击叶子节点选中，点底部「选择」确认

#### Step 4：1688 参数提取
- 用 `ctx.new_page()` 在新标签页打开 1688 URL
- 从嵌入JSON正则提取参数，详见 `references/1688-json-extraction.md`
- 从页面文本提取：货号（商品编码前缀）、重量、品牌、材质等

#### Step 5：产品属性

**⚠️ 2026-07-19 方法更新：JS强制显示dropdown+点击（替代CDP坐标法）**

详见 `dxm-attributes` skill（以该skill为准，它是属性的权威模块）。

核心方法：
```javascript
// 找含目标选项的dropdown → 强制显示 → 点击
dd.classList.remove('ant-select-dropdown-hidden');
dd.style.display = ''; dd.style.opacity = '1'; dd.style.pointerEvents = 'auto';
item.click(); item.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
```

**检测带星号字段：** 使用 `span.attr-label.required`（不是 `.ant-form-item-required`）。

**🚨 auto-complete 型字段填充方法（2026-07-19 攻克）：** `ant-select-auto-complete` 型字段（如最大出餐量、材质）可用 **Playwright keyboard.type() + 点空白处blur（不提Enter）** 填充。详见 `dxm-attributes` skill pitfall #9。值存储在 `input.value` 而非 `.ant-select-selection-item`，验证时需分别检查。

**验证规则：** 只有**所有**带星号字段都填完才算通过。7/9 ≠ 完成，8/9 ≠ 完成。必须9/9。验证时注意 `ant-select-auto-complete` 型字段值在 `input.value` 中（不在 `.ant-select-selection-item`），需分别检查。

#### Step 6：删除自定义属性
- 属性信息 tab → 自定义属性区 → 批量操作 → 删除全部

#### Step 7：产品图片（含子步骤7.1-7.8）
详见 `references/sku-table-fields.md` 图片处理章节

#### Step 8：SKU定价栏

**术语定义：** SKU定价栏 = 零售价 + 货值 + 库存 + 长/宽/高 + 包装尺寸 + 是否原箱 + 物流属性 + 商品编码

**字段规则：**
| 字段 | 规则 |
|:--|:--|
| 零售价(CNY) | **= 货值。不等于1688成本价！** 按定价公式计算 |
| 货值(CNY) | **= 零售价**（两列填同一个数） |
| 库存 | 1688库存>2000封顶写2000，≤2000如实写 |
| 重量(kg) | 从1688提取 |
| 包装尺寸(cm) | 有数据则填，无跳过 |
| 是否原箱 | 原生select，设为「是」(value=1) |
| 物流属性 | 无电→普货；有电→内电 |
| 商品编码 | 一键生成，1688有货号填前缀 |

**定价公式：**
```
零售价 = 货值 = (1688成本价 + 国内运费¥5) × 1.02 ÷ [0.70 × (1 - 21% - 净利率)]
       = (成本 + 5) × 1.02 ÷ 0.413  （净利率20%时）
```
- 国内运费固定：**¥5.00** | 退货率2% | 平台费率30% | 其他费率21%
- 净利率：起量/引流款=20%, 利润款=30%, 新品=20%

**操作序列：**
- **8a 批量填写：** 批量行填零售价/货值/库存/重量 → 点「批量填充」
- **8b 是否原箱：** Playwright `select_option('1')` 设为「是」
- **8c 物流属性：** 点「批量」→ 弹窗选 checkbox → 点确定
- **8d 商品编码：** 点「一键生成」→ 有货号填前缀 → 点设置
#### Step 8.5：PC端描述

详见 `references/pc-description-template.md`

- **⚠️ 两个「批量编辑图片」陷阱：** CKEditor 工具栏中有两个同名的「批量编辑图片」元素。CKEditor 内置 combo（类 `cke_combo`）点击后打开空面板——**不要点这个！** 真正的按钮在展开图片栏后的 `images-options` 区域（类 `ant-dropdown-trigger`）
- **展开图片栏（前置！）：** 批量编辑图片按钮默认隐藏，必须先点击 CKEditor 工具栏最右侧的「展开图片栏」（`.cke_button__imagepaneltoggle`）使其可见。CKEditor 按钮用 `element.dispatchEvent(new MouseEvent('mousedown',{bubbles:true}))` + `.dispatchEvent(new MouseEvent('mouseup',{...}))` + `.dispatchEvent(new MouseEvent('click',{...}))` 触发
- **引用模板：** 描述信息 tab → CKEditor → 工具栏「引用模板」→ 选模板 → 选择
- **批量改图片尺寸精准步骤（用户2026-07-18验证的完整7步序列）：**
  1. **滚动到合适位置：** 将 `.images-options` 按钮滚到视口 y≈400-700 的位置（`window.scrollBy(0, r.top - 400)`）
  2. **点开下拉：** 用 `Input.dispatchMouseEvent(mousePressed → mouseReleased)` 在按钮坐标上触发——JS `.click()` 对 antd 无效
  3. **选「批量改图片尺寸」：** `.ant-dropdown-menu-item` textContent 匹配
  4. **弹窗出现后→下拉1从「等比例调整」改为「自定义比例调整」：** 用 `Input.dispatchMouseEvent` 点击 `.ant-select-selector` 坐标，然后在打开的 `.ant-select-dropdown` 中点 `.ant-select-item`（textContent === '自定义比例调整'）——默认是等比例，不切换则没有完整宽高输入
  5. **图片宽填800：** 找到 `input[name=valueW]` 填 800（用 nativeValueSetter + dispatchEvent）
  6. **选择全部：** 点 `.ant-checkbox-wrapper` 中 textContent 包含「选择全部」的 label
  7. **生成JPG图片：** 点 button 中 textContent 包含「生成JPG」的按钮
  ⚠️ **铁律：以上7步必须严格按顺序，每步做完等用户确认看到变化，再走下一步。不许跳步，不许猜下一步。**
- **图片翻译操作流程（2026-07-18新增）：** 与批量改尺寸同入口，dropdown 选「图片翻译」。详见 `references/pc-description-template.md`「PC端描述—图片翻译操作流程」
- **⚠️ 绝对定位偏移陷阱（高频坑）：** ant-dropdown 和 ant-select-dropdown 使用绝对定位（`top: 5136-5612px`），当页面滚动到下方时菜单渲染在视口外。**解决方案：** 点按钮前先 scroll 使按钮在视口 y≈400-700（预留下拉空间），然后 mousePressed+mouseReleased 点击。验证：dropdown 的 `display!=='none'` 但 `getBoundingClientRect` 全零 → 还在视口外 → 重新 scroll 并重试
- **用户铁律：每一步操作要让用户看到变化。** 点完「批量编辑图片」后让用户确认看到下拉菜单→再点「批量改图片尺寸」→确认看到弹窗→再改下拉→确认看到自定义比例→填800→确认看到数→选全部→确认→生成JPG。**每做完一步汇报，等用户说"继续"或给下一步指令再动。** 不要自己一次性操作完所有步骤。
- **用户铁律：不要猜下一步。** 严格遵守用户说一步你做一步的顺序。"你要按照我的步骤来，不可以猜"——填800、选全部、生成JPG这三步必须由用户逐个指示，不能一次性批量做完。

#### Step 9：保存并移入待发布
所有字段填写完成后，点击页面顶部右侧的「保存并移入待发布」按钮。

**两种入口路径：**
- **路径 A（直接编辑）：** 采集箱 → 编辑 → 填完 → 保存
- **路径 B（先移后改 — 推荐）：** 采集箱 → 移入待发布（弹窗点「确 定」字中间有空格）→ 待发布列表 → 编辑 → 填完 → 保存

## 🖱️ CDP 三击全选
详见 `references/step-by-step-mode.md`

## 🧠 工作流智慧

### 🔴 铁律：上架流程未完成前，禁止启动新分析/调研任务

**用户2026-07-18明确纠正：**「为什么你突然去看谷歌趋势了？我们的上架流程还没有操作完。你错乱了，需要先完成上架工作流」

**规则：**
- 上架工作流（Step 0 → Step 9）进行中时，**绝对禁止**中途切换去做市场分析、谷歌趋势、竞品调研等任何非上架任务
- 即使上架过程中遇到失败/卡住（如翻译失败），汇报给用户等待指示，**不要自己决定「换一件事做」**
- 所有调研/分析/规划类任务，**只在没有进行中的上架流程时**才启动
- 用户说「算了，你换一件事做吧」= 跳过当前卡住的步骤继续上架流程，**不是**换项目去谷歌趋势
### 🚫 不要问「下一步做什么」——skill里已经全有了

**用户2026-07-18明确纠正：**「我不想再看到你问我任何问题。因为你总结的skill里面已经全部都有了。」

**规则：**
- Skill已经把15步流水线、每步的字段规则、已知坑点都写全了。执行时**不要停下来问「下一步做什么」「这个属性怎么填」**
- 有不确定的属性值？从1688参数推断最接近的（产地=浙江因义乌、品牌=NONE、材质=硅胶等），填完让用户检查
- 唯一需要问的情况：skill未覆盖的新步骤/新场景，或者同一操作3次失败（三振出局）
- **流畅执行 > 等待确认**。用户宁愿你填错他纠正，也不想一步一问

### 🚫 绝对禁止编造/曲解用户的话
**用户2026-07-18明确纠正：**「我确定我没有说过让你去做另外一件事情。你以后不许跟我撒谎，因为我会查看我们的聊天记录。」
- 用户说什么就是什么。不要把沉默/叹息/「算了」解读成自己想要的指令
- 每次说自己做某事的理由时，确保这句话真的出自用户之口——用户会查聊天记录核实
- 没听清就再问，不许编造「用户说过xxx」来合理化自己的行为

### 🚫 delegate_task 会覆盖 CDP 浏览器的标签页（2026-07-18新增）

**发现：** 代理任务（`delegate_task`）调用 `browser_navigate` 或 `browser.new_page()` 时，会在**用户 Chrome 的同一个 CDP 上下文**中创建新页面。如果 CDP 浏览器原本只有 2-3 个标签页（1688 + 店小秘编辑页），新页面可能覆盖编辑页标签，**导致编辑页丢失，全部未保存数据丢失**。

**规避规则：**
- 上架流程进行中，**禁止**调用 `delegate_task` 执行任何涉及浏览器操作的任务
- 必须用 `delegate_task` 时，确保任务只使用 `web_search` / `terminal` / `curl`，**不碰浏览器**
- 如果 CDP 编辑页已被覆盖，先确认用户看到了什么（用户可能已自己重新打开），然后用 CDP 导航回店小秘采集箱重新进入编辑页
- **安全替代方案：** 需要并行调研时，优先用 `web_search` + `curl` 或 `execute_code` 而非 `delegate_task`

## 🛠️ 编辑页丢失恢复流程（2026-07-18新增）

**场景：** 编辑页因意外关闭/标签页被覆盖/delegate_task干扰导致丢失，所有未保存数据可能丢失。

**恢复步骤：**

1. **检查 CDP 中是否还有编辑页 target**（通过 `Target.getTargets` 找 title="店小秘--编辑速卖通产品" 的 target）
2. **如果有编辑页 target**：直接用 `Runtime.evaluate` 评估页面状态，可能页面还在只是 Playwright 连接断开
3. **如果没有编辑页 target**（页面已关闭）：重新导航到采集箱
   - **采集箱 URL：** `https://www.dianxiaomi.com/web/smt/smtProductList/draft`
   - **全托管采集箱：** `https://www.dianxiaomi.com/web/smtChoice/draft`
4. **找到产品并再次编辑：**
   - 在表格中按产品标题文本找到对应行
   - 点击该行的「编辑」链接（`<a>编辑</a>`）
   - 注意：编辑链接会在**新标签页**中打开编辑页（`smt/edit?id={product_id}`）
5. **导航到所需 tab：** 编辑页左侧的 tab 用的是 `div.anchor-menu-item`（不是 `.ant-tabs-tab`），点击文本匹配的锚菜单项跳转
6. **检查数据是否持久化：** 之前填过的数据（标题/分类/SKU/PC描述等）可能已部分持久化到服务端。用 `page.evaluate` 读取各输入框的值判断哪些字段需要重填
7. **PC端描述通常持久化最好：** 本次验证中，页面关闭重开后 PC端描述内容（3278字符）仍然保留。但图片修改（改尺寸/翻译/营销图）一般需要重做

**⚠️ 重要：** 编辑页关闭后会丢失的数据：
- 产品图片的选择状态（需重新选主图）
- 营销图片（需重新一键生成）
- 图片翻译进度（需重新翻译）
- SKU图片的改尺寸状态
- 批量改图片尺寸后的图片

### 🚫 永远不要问用户"你要不要自己操作"
**用户铁律：**「你自己想办法」= 自己搞定。能填的全填上，最后汇报时可以说「这些字段CDP搞不定，你手动点一下」但不能问「你要不要自己操作」

### 🚫 三振出局原则
同一操作3次不成功 → 立即停手汇报。不要换第4、第5种方法继续试。

### 🎯 先出流程图再执行
涉及新工作流时：先做流程图 → 用户审核 → 确认后再执行。

### 📋 上架操作铁律
1. 编辑页绝不刷新/重开
2. 来源URL「访问」必须开新标签页
3. 查数据开新标签页，查完切回编辑页
4. 一条 Playwright 会话一条龙到底
### 🔴 CDP 操作可见性铁律（2026-07-18 重要更新）

**核心问题：** Playwright 通过 CDP 操作店小秘时，DOM 修改可能不被 Vue 3 的响应式系统捕获，导致用户页面看不到变化——即使代码执行成功。

**用户明确要求：「你以后都要显示出来，不然的话我不知道你进行到哪一步了」**

**用户明确要求：「你要按照我的步骤来，不可以猜」**——每步做完汇报，等用户指示下一步。不要一次性操作多步。

**解决方式（按优先级）：**

1. **🥇 最高优先级：** 每次操作后**必须**让用户看到页面变化。不要在后台默默执行多步操作。用户说看不到立即停手，换真实交互方式重做，而不是换 JS 方式继续试。

2. **🥈 CDP Input.dispatchMouseEvent（antd 组件首选）：** 对 ant-design 组件（`.ant-dropdown-trigger`, `.ant-select-selector` 等），JS programmatic `.click()` 无效。必须在浏览器_cdp 工具中用 `Input.dispatchMouseEvent(type='mousePressed', x, y)` + `Input.dispatchMouseEvent(type='mouseReleased', x, y)` 在按钮实际坐标上触发真实鼠标事件。
   - ⚠️ **重要：点之前先滚动按钮到视口中部（y≈400-700）**，否则 antd 渲染的 dropdown 在视口外（绝对定位 top: 5612px 等），用户看不到下拉菜单
   - 用 `window.scrollBy(0, r.top - 400)` 将按钮定位到视口上部

3. **🥉 Playwright page.mouse.click() + page.keyboard.type()：** 用真实鼠标点击 + 键盘输入代替 JS setter/dispatchEvent。`page.mouse.click()` + `page.keyboard.type()` 能触发最完整的浏览器事件链。

4. **❌ 避免的写法（已被证明对 Vue 3 + antd 无效）：**
   - `element.click()` (JS programmatic)
   - `Runtime.evaluate` 里的 `.dispatchEvent(new Event(...))` 
   - `nativeInputValueSetter` + `dispatchEvent('input')`
   - `DOM.setFileInputFiles`（Vue 重渲染清除文件）

5. **验证方法：** 每次 click 后检查弹出的 ant-dropdown/ant-select-dropdown 的 `getBoundingClientRect()`。如果 `display` 为 `block` 但 `rect` 为空数组（全零），说明 dropdown 被渲染到视口外——scroll 重试。

## 🚨 颜色配置规则
- 自定义名称：只保留颜色英文名，去掉中文前缀
- 例：「宠物户外喂水碗【绿色】」→「Green」
- SKU 图片翻译：仅含中文时执行，否则跳过
- 颜色SKU图改尺寸入口：颜色 SKU 区蓝色「批量」链接

## 💲 定价公式（更新于2026-07-18）
```
零售价 = 货值 = (1688成本价 + 国内运费¥5) × 1.02 ÷ [0.70 × (1 - 21% - 净利率)]
```
- **关键纠正：** 零售价=货值，不等于1688成本价！国内运费固定¥5

## 🔋 物流属性判断
| 产品类型 | 物流属性 |
|:--|:--|
| 无电（硅胶碗、普通日用品） | 普货 |
| USB充电（风扇、净化器） | 内电→非纽扣锂离子电池 |
| 纽扣电池（LED灯） | 内电→纽扣式锂电池 |
| 干电池（遥控器） | 内电→干电池 |
| 充电宝/电池盒 | 内电→非纽扣锂离子电池 |

#### Step 6：删除自定义属性
- **「确 定」按钮文本含空格：** 删除确认弹窗中的按钮文字为「确 定」（中间有空格），与 Step 9 的移入待发布弹窗同理。用 `btn.innerText.trim() === '确 定'` 匹配，不要 trim 后等于 '确定'（匹配失败）
- 路径：自定义属性区 → 批量操作 → 删除全部 → 弹窗点「确 定」
- 弹窗确认后关闭，验证自定义属性区是否已清空

## 已知坑点速查
1. 是否原箱用原生 `<select>`，不用 ant-select，JS 改 value 可能不被 Vue 捕获 → 用 Playwright `select_option()`
2. 物流属性弹窗用 `.ant-checkbox-wrapper` 精确匹配
3. 商品编码必须先设物流属性，否则报错
4. 定价公式：国内运费固定¥5，不是0
5. 标签页管理：每次进编辑页前清理多余的重复标签页
6. 用户说「是否原籍」= 是否原箱（语音识别差异）
7. PC描述批量改尺寸有3个下拉（产品主图只有2个），下拉2/3联动自动变化。批量编辑图片按钮默认隐藏——必须先点「展开图片栏」
8. **CKEditor两个「批量编辑图片」陷阱（高频坑）：** 工具栏中同时存在 `cke_combo`（CKEditor原生combo，打开空面板）和 `images-options` 内的 `ant-dropdown-trigger`（真正的菜单）。必须在展开图片栏后，点击 `images-options` 区的按钮。误点cke_combo则用Esc关闭空面板
9. **ant-dropdown绝对定位偏移（高频坑）：** images-options的批量编辑图片ant-dropdown菜单使用 `style: top: 5612px` 绝对定位，可能落在视口外。**正确做法：** 用 `getBoundingClientRect()` 找到按钮坐标，`window.scrollBy(0, r.top - 400)` 将按钮移到视口中部（y≈400-700），然后用 `Input.dispatchMouseEvent(type='mousePressed', x, y)` + `(type='mouseReleased', x, y)` 在按钮坐标处触发真实鼠标事件。验证：dropdown `display!=='none'` 但 `rect` 全零 → 仍在视口外 → 重新scroll。ant-select-selector（弹窗内下拉）同理需要坐标级 mousePressed+mouseReleased。
10. **CDP操作可见性（高频坑）：** `page.evaluate()` 改DOM或JS dispatchEvent可能不被Vue捕获。必须用真实鼠标交互。**已验证有效的CDP click序列：** ①获取按钮 `getBoundingClientRect` 坐标 ②`window.scrollBy(0, r.top - 400)` 将按钮移到视口中部 ③`Input.dispatchMouseEvent(type='mousePressed', x, y)` ④`Input.dispatchMouseEvent(type='mouseReleased', x, y)`。此方法对 `ant-dropdown-trigger`（images-options）和 `ant-select-selector`（弹窗内下拉）均有效。做完一步**必须**让用户确认看到变化再继续下一步。**不许猜下一步，用户说一步你做一步**。
11. **ant-select下拉残留（高频坑-2026-07-18新增）：** 多个ant-select连续操作时，前一个dropdown在DOM中残留并拦截后续select的click事件。**必须八字诀：点→选→Esc→移动。** 要点：点击打开dropdown→选择值→Escape关闭→再移动鼠标到下一个select的坐标并点击。`Input.dispatchKeyEvent(type='keyDown', key='Escape')` + `(type='keyUp', key='Escape')` 在select操作之间清场。缺少这一步会导致后续所有select都打在上一个下拉的遮罩上。
12. **图片翻译「一键翻译」≠「快速翻译」（2026-07-18新增）：** 图片翻译弹窗中有两个容易混淆的元素：**「快速翻译」** 是 checkbox toggle（默认已勾选），**不是操作按钮**；真正提交翻译的按钮是 **「一键翻译」** （`.ant-btn-primary`，文本「一键翻译」）。**错误操作：** 点了「快速翻译」checkbox 然后等翻译 → 没用，因为这只是个模式开关。**正确操作：** 确认「快速翻译」已勾选（不用动它），然后点**「一键翻译」**按钮。
13. **图片翻译「投递失败」错误（2026-07-18新增）：** 点击「一键翻译」后可能提示「投递失败」。原因：①店小秘翻译账号暂无额度（按张收费）；②图片此前已翻译过，系统拒绝重复翻译。**解决方案：** 如果提示失败，不要反复点击——先检查图片是否已经是英文版（可能之前已翻译过了），然后向用户汇报。**不要浪费翻译配额。**
14. **部分非星号下拉字段对所有自动化方法免疫（2026-07-19新增）：** 属性信息中的非星号字段（如电源/Power Source、电压/Voltage、动力来源/Power Source）的下拉选项无法通过任何已知方法选中：CDP `Input.dispatchMouseEvent` 坐标点击 ✅ 能打开 dropdown ❌ 选中后值不持久化；Playwright `mouse.click()` 同上；Playwright `locator.click()` 同上；`keyboard ArrowDown+Enter` 同上；JS `element.click()` 同上。疑似 Vue 3 select 组件的内部状态不响应外部事件。**策略：优先填星号字段，非星号字段跳过不纠缠。超过3次尝试不成功立即停手，汇报给用户手动选。**
15. **execute_code + websocket CDP 全页QA扫描（2026-07-19新增）：** `browser_snapshot` 截断在约1500行，无法覆盖编辑页下半部分（SKU表、描述、包装、模板等）。**替代方案：** 用 `execute_code` + Python `websockets` 库直连 `ws://127.0.0.1:19223/devtools/page/{targetId}`，发送 `Runtime.evaluate` CDP命令执行 JS 表达式扫描页面全部数据（`document.querySelectorAll`、`document.body.innerText` 等），返回结构化 JSON。此法可一次性扫描所有带星号字段、请选择数量、body文本长度等，不受视口截断限制。详见 `references/cdp-websocket-qa-scan.md`。
16. **🔴 店小秘公告弹窗拦截（2026-07-19重大发现）：** 店小秘不定时弹出全屏公告弹窗（`ant-modal-wrap notice-list-modal`），会拦截**所有** Playwright `locator.click()` 操作（元素可见但 pointer events 被弹窗拦截，30秒超时）。但 JS `evaluate` 操作不受影响。**解决方案：** 每次开始编辑前，先执行 JS 强制清除所有弹窗：`document.querySelectorAll('.ant-modal-wrap, .notice-list-modal, .bullet-layer').forEach(m => m.remove())`。如果清除不彻底（弹窗按钮的click不触发Vue），关掉后再用 `locator.click({force: true})`。
17. **🔴 品牌制造商填完后品牌必验证（2026-07-19血训）：** 填完品牌制造商（keyboard Enter）后，品牌字段可能被随机覆盖为制造商的值（如 Shaoguan Jiuye Technology Co., Ltd）。**必须在 save 之前验证品牌仍为 NONE(NONE)，如果不是则重新修正。** 此问题发生了至少 3 次。
18. **属性下拉填充——唯一有效方法（2026-07-19反复验证）：** 在常规情况下（无弹窗拦截），最可靠的方法是 `selector.dispatchEvent(new MouseEvent('mousedown', {bubbles: true})); selector.dispatchEvent(new MouseEvent('mouseup', {bubbles: true})); selector.click()` 打开 dropdown，然后 `item.click()` 选选项。但此方法在共享下拉池场景下不可靠（可能点到错误的dropdown）。**如遇连续失败，不要死磕属性字段，先填其他模块**，最后汇报给用户手动修正。
19. **browser_navigate/snapshot auto-launch 404（2026-06-14新增）：** CDP 中继链正常但 Hermes browser 封装工具报 `Auto-launch failed: CDP WebSocket connect failed: HTTP error: 404 Not Found` 时，`browser.engine: cdp` 也无法解决。回退到纯 `browser_cdp` 工具操作（`Target.getTargets`, `Page.navigate`, `Runtime.evaluate`, `Target.createTarget`, `Page.captureScreenshot` 等）。完整操作指南见 `references/cdp-direct-operation.md`。
17. **「保存并移入待发布」按钮对所有automation方法免疫（2026-07-19发现）：** 该按钮不响应 CDP `Input.dispatchMouseEvent`、Playwright `mouse.click()`、JS `element.click()`、`dispatchEvent`、keyboard Enter 等任何已知方法。疑似Vue 3 + ant-modal-wrap双重拦截。**「保存」按钮可用（Playwright mouse.click有效）。流程改为：自动化填完所有字段 → 点「保存」→ 通知用户手动点「保存并移入待发布」。**
18. **Playwright connect_over_cdp 连接范围（2026-07-19新增）：** `connect_over_cdp('http://127.0.0.1:19223')` 连接Chrome的CDP端点后，`browser.contexts[0].pages` 返回所有打开的标签页。不需要通过Target.getTargets + activateTarget来切换——直接用 `for pg in browser.contexts[0].pages` 找到目标页并操作。但每个page对象已绑定固定target，操作前务必确认 `pg.url` 匹配。
19. **browser_navigate/snapshot auto-launch 404（2026-06-14新增）：** CDP 中继链正常但 Hermes browser 封装工具报 `Auto-launch failed: CDP WebSocket connect failed: HTTP error: 404 Not Found` 时，`browser.engine: cdp` 也无法解决。回退到纯 `browser_cdp` 工具操作（`Target.getTargets`, `Page.navigate`, `Runtime.evaluate`, `Target.createTarget`, `Page.captureScreenshot` 等）。完整操作指南见 `references/cdp-direct-operation.md`。
16. **品牌字段被品牌制造商覆盖（2026-07-19新增）：** 当「品牌」选NONE后填「品牌制造商」时，品牌制造商的下拉打开+keyboard Enter可能误触品牌字段（两者在同一视口区域内）。**规则：填完品牌制造商后立即验证品牌字段仍为NONE。** 如被覆盖，重新对品牌选NONE。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*