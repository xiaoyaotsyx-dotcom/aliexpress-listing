# 店小秘发布检查清单

> 用户（老板）制定的完整上架流程，按 Step 分步 + 按 Section 逐项填写。
> **顺序不可乱**。先执行 Step 0→1→2 进入编辑页，再按 Section A-I 逐个 tab 填。

## 总体流程（Step 系统）

新版上架流程已拆分为**分步操作 Step 0-2** + **Section A-I 检查清单**两步走：

**先走 Step 体系：**
- **Step 0 → 进入采集箱**：左侧菜单「产品」→「采集箱」→「速卖通」采集箱 (N个)
- **Step 1 → 点「编辑」进入编辑页**：在采集箱列表点目标产品的「编辑」，新标签页打开
- **Step 2 → 标题改英文**：进入编辑页后，第一时间将中文标题改为纯英文

**再走 Section 体系（以下 A-I 清单）：**
- 按 Tab 顺序逐项检查填写
- 全部填完后点「保存并移入待发布」
- 通知用户检查 → 用户确认后再发布

> 📎 完整分步操作流程见 SKILL.md「上架流水线 — 分步操作流程」章节
> 📎 可视化流程图：`references/listing-flow.excalidraw`（拖到 excalidraw.com 查看）

---

## Section A：基本信息

### A1 标题
- [ ] 128字符内
- [ ] **不得含中文**（含中文字符发布失败）
- [ ] 英文关键词，参考产品标题结构
- [ ] 格式：`[特性1] [特性2] ... [品名] for [场景1] [场景2] [场景3]`
- [ ] 示例：`Mini Necklace Air Purifier USB Rechargeable Negative Ion 36dB Silent Portable Personal Air Purifier for Travel Office`

### A2 产品分类
- [ ] 4级类目路径
- [ ] 与速卖通推荐分类一致（不一致时发警告，需确认）

---

## Section B：产品属性

### B1 属性信息
- [ ] **所有带星号(*)的属性必须填写**，不可跳过
- [ ] 不带星号的属性：1688提供了就填，没有就不填
- [ ] 品牌(Brand Name)：选 NONE(NONE)（除非有品牌）
- [ ] 电压(Voltage)：USB设备选 DC5V(DC5V) 或 5V(5V)
- [ ] 产地(Origin)：中国大陆(Mainland China)
- [ ] 风量(Air Volume)：按1688数据（50m³/h → 50立方米/小时）
- [ ] 功率(Power)：USB小设备选 1瓦(1w)
- [ ] HEPA滤网等级：无HEPA选 NONE(NONE) 或 其他(Other)
- [ ] 高关注化学品：选 天然未处理(None)
- [ ] 噪音(Noise)：按1688数据（36dB以下 → ≤35分贝(≤35dB)）
- [ ] 认证(Certification)：按1688数据选（CE/ROHS等可多选）
- [ ] 物流属性(Battery等)：有电的产品选电池类型
- [ ] 电源方式(Power Supply)：USB/电池供电

### B2 自定义属性
- [ ] **全部删除，不要留**（用户说没用）
- [ ] 1688导入的冗余属性（噪音/颜色/功能等标准属性已有就删）
- [ ] 删除方法：点 **「批量操作」** → **「删除全部」** → 弹窗点 **「确 定」**（不要逐个点删除按钮）
  - ⚠️ 按钮文字「确 定」中间有空格，用 `.includes('确')` 匹配

### B3 属性值不匹配的处理
- [ ] 1688的中文值可能与AliExpress选项不同，选最接近的
- [ ] 例：1688写"36dB以下"→ AliExpress选"≤30分贝"
- [ ] 无法配对的属性值可在产品描述中补充说明

---

## Section C：产品图片

### C1 主图
- [ ] **6张**（最多6张，检查「已经选用了 X 张」说明文字）
- [ ] 全部**800×800**尺寸
- [ ] **批量改图片尺寸**（通过 PC端描述 CKEditor →"批量编辑图片"→"批量改图片尺寸"→ 800px → 选择全部 → 生成JPG图片）
  - ⚠️ CKEditor 面板在 `iframe.cke_panel_frame`，用 Playwright `frame_locator` 访问
- [ ] 图片清晰，不能模糊
- [ ] **不得含中文文字**，必须是英文
- [ ] 不要打水印（除平台自动水印外）
- [ ] 每张图展示不同角度/细节（正面/背面/侧面/细节/使用场景/包装）
- [ ] 图片尺寸验证：看 `选用 800 X 800` 字样

### C2 营销图片
- [ ] **白底图**（1:1比例）→ 点**「一键生成」**按钮，尺寸800×800
- [ ] **场景图**（3:4比例）→ 点**「一键生成」**按钮，尺寸750×1000
- [ ] 注意：部分分类不支持营销图，按平台规则

### C3 商品说明书
- [ ] 用户提供文件后上传（通常从桌面获取）
- [ ] 路径：`/mnt/c/Users/[你的Windows用户名]/Desktop/风扇说明书.pdf` 等

**上传步骤（CDP鼠标事件方式 — 2026-06-15 已验证）：**

> ⚠️ Ant Design Dropdown 在 CDP 模式下用普通 JS `.click()` 无法打开下拉菜单（React 事件绑定问题）。必须用 CDP `Input.dispatchMouseEvent` 坐标点击。

1. 滚动到「商品说明书」区域
2. 获取「上传文件」按钮在视口中的坐标
3. 用 CDP 鼠标事件点击按钮坐标（先 mousePressed 再 mouseReleased）
4. 等待 800ms，找到 `.ant-dropdown-menu-item` 中可见的选项
5. 用同样方式点击 **「图片空间(PDF)」** 选项
6. 在图片空间弹窗中找到 PDF 文件并点击选中
7. 点击弹窗「确定」按钮

**备用方案（CDP `DOM.setFileInputFiles`）：**
```javascript
// 1. 通过 CDP DOM.querySelector 找到 #localFileUploadInp
// 2. DOM.setFileInputFiles(nodeId, files=["/path/to/风扇说明书.pdf"])
// 3. 通过 CDP Runtime.evaluate 触发 change 事件：
document.getElementById('localFileUploadInp')
  .dispatchEvent(new Event('change', {bubbles: true}));
// 注意：此方式可能使页面卡死（上传处理阻塞），优先用图片空间(PDF)方式
```

**注意点：**
- 按钮点击后弹出的下拉菜单有3个选项：本地上传 / 上传URL链接 / 图片空间(PDF)
- 必须选「图片空间(PDF)」，因为店小秘的文件上传通过图片空间管理
- 文件已在图片空间中（之前用 `#localFileUploadInp` 的 `set_input_files` 会上传到图片空间，但不会自动绑定到商品说明书槽位）
- 弹窗中每行显示 `点击选中 文件名.pdf--大小`，点击即选中
- 如果弹窗中已有文件但未出现，是因为先前的文件上传已存入图片空间但未绑定到当前商品的说明书槽位
- 如果暂时没有说明书PDF，可以先点「保存」（非强制校验）存草稿，下次再补

---

## Section D：产品视频

### D1 视频来源
- [ ] 优先从1688产品页面获取
- [ ] 1688视频URL格式：`https://cloud.video.taobao.com/play/u/{user_id}/p/2/e/6/t/1/{video_id}.mp4`
- [ ] 可在1688页面的HTML源码中搜索 `.mp4` 或 `cloud.video.taobao.com` 找到
- [ ] 也可以在其他链接找同款产品的视频
- [ ] 区别：**产品本身的视频**（展示产品功能/使用），**不是工厂视频**（展示生产线/工厂环境）
- [ ] 视频不应带工厂logo

### D2 上传到店小秘
- [ ] 下载视频到 `/mnt/d/`（Windows可访问路径）
- [ ] 通过 `#localFileUploadInp` 文件输入框上传
- [ ] 上传后确认状态：显示「审核成功」或出现「播放」按钮
- [ ] 视频限制100M内，建议1:1或9:16比例

---

## Section E：SKU配置

### E1 颜色/变种
- [ ] 按1688产品的颜色设置（如：白色/黑色/银色）
- [ ] 每个颜色作为一个SKU变种
- [ ] 注意：部分颜色值可能显示「该属性值平台已废弃，不支持选择」— 需选正确的有效颜色
- [ ] 3个颜色起配，不多于5个（同店铺成熟产品的模式）

### E2 自定义名称（英文）
- [ ] 白色 → White
- [ ] 黑色 → Black
- [ ] 银色 → Silver
- [ ] **文字必须是英文**

### E3 颜色图片
- [ ] 每个颜色SKU配一张图片
- [ ] 图片800×800尺寸
- [ ] 图片展示该颜色的产品实物

### E4 零售价
- [ ] **必须用 SKILL.md 中的「定价策略 — 公式法」计算，不得再用 3x 估算法**
- [ ] 标准公式：`定价 = ((成本+运费) × (1+退货率)) / ((1-折扣率) × [1-(平台佣金+联盟佣金+营销费+目标净利率)])`
- [ ] 默认参数在 SKILL.md 定价策略章节
- [ ] 计算示例：成本¥20.88、运费¥0、目标净利率20% → ¥52
- [ ] **成本 = 当前SKU中1688的零售价**（即1688导入时的价格），不是独立输入的变量
- [ ] 成本不一定固定，不同产品1688价格不同，每次按实际算
- [ ] 目标净利率按品类定位选：起量20% / 利润款30% / 新品40%

### E5 货值
- [ ] **货值跟零售价保持一致**

### E6 库存
- [ ] **必须用1688原始库存数据，不得随意写数字**
- [ ] 打开1688产品页，搜索各颜色的「库存N件」数值
- [ ] 规则：1688库存 > 2000 → 写2000（封顶）；≤2000 → 如实写
- [ ] 例：白色库存78,656件、黑色52,272件、银色79,285件 → 全部写2000
- [ ] 注意：1688导入后库存字段会被填为1688产品ID而非实际库存数，必须覆写

### E7 重量
- [ ] 从1688包装信息表中找
- [ ] 1688格式：`颜色 | 长(cm) | 宽(cm) | 高(cm) | 体积(cm³) | 重量(g)`
- [ ] 填进入口：`重量(kg)`字段
- [ ] 例：1688写45g → 填0.045（净重）或0.080（含包装余量，用户选择）
- [ ] 注意：重量用kg单位，45g=0.045kg

### E8 包装尺寸
- [ ] 优先用1688数据（6×3×2cm）
- [ ] 没有的话写 15×15×15
- [ ] 入口：`长` `宽` `高` 三个独立字段

### E9 是否原箱
- [ ] **全部选「是」**（包含全局行 + 所有SKU行）
- [ ] ⚠️ 共4个select需设置（索引1,2,3,4），不要只设3个
- [ ] 验证方法：`Array.from(selects).slice(1,5).map(s => s.selectedIndex)` 都==2

### E10 物流属性
- [ ] 点表头 **物流属性 → (批量)** 打开批量编辑Modal
- [ ] 按产品实际电池类型选择（详见 `references/sku-variant-config.md` 电池选择表）
- [ ] USB充电内置锂电池产品 → **内电 → 非纽扣锂离子电池**
- [ ] 必须先设✅才能生成商品编码（否则报「物流属性必填！」）
- [ ] 批量设置自动应用到所有SKU行

### E11 商品编码
- [ ] **必须**先设完物流属性再操作
- [ ] 打开1688产品页搜索 **货号/型号/产品编号**
- [ ] **有货号** → 点击「一键生成」→ 输入货号为前缀 → 点「设置」
- [ ] **无货号** → 点击「一键生成」→ 留空前缀 → 直接点「设置」

### ✅ 区域调价
- [ ] **不用管**（跳过）

---

## Section F：描述信息

### F1 PC端描述
- [ ] **不得含中文**（全部英文）
- [ ] 所有图片尺寸800×800
- [ ] 包含：产品功能属性、产品细节图片、支付物流、售后服务、公司实力
- [ ] 可以用1688的产品描述图片（去掉中文的）
- [ ] 通常包含6-8张详情图

### F1b 引用模板（关联营销模块）
- [ ] 点CKEditor工具栏 **「引用模板」** 按钮
- [ ] 在对话框列表中找到目标模板（如 mini fan）
- [ ] 勾选该行操作列的 checkbox → 点 **「选择」**
- [ ] 验证：模板加载到编辑器中（图片明显增多）
- [ ] 详细操作见 `aliexpress-listing → references/pc-description-template.md`

### F1c 批量改图片尺寸（重要！）
- [ ] 点CKEditor工具栏 **「批量编辑图片」** combo
- [ ] 选 **「批量改图片尺寸」** 菜单项
- [ ] 弹窗配置：**自定义比例调整 → 图片宽 → 800**
- [ ] 勾选 **「选择全部」**
- [ ] 点 **「生成JPG图片」**
- [ ] 验证：所有描述图片宽度变为 800px
- [ ] 详细操作见 `aliexpress-listing → references/pc-description-image-resize.md`

### F2 无线端描述

⚠️ **必须严格按以下顺序操作（已验证 2026-06-08），错一步弹窗堆叠！**

1. [ ] 滚动到「无线端描述」区域，点击 **「使用新版编辑器」** 绿色按钮（`button.btn-green.w-150`，白字）
   - ⚠️ 如果编辑器容器隐藏（`display: none`），先点「使用老版编辑器」radio → 再点回「使用新版编辑器」
2. [ ] 新版编辑器弹窗在**页面顶部**弹出，标题栏右侧有蓝色 `span.link` **「根据PC端描述一键生成」**
3. [ ] 点击 **「根据PC端描述一键生成」** → 弹出确认框「一建生成将会替换掉现有的无线端内容...」
4. [ ] 点击确认弹窗中的 **「确 定」**（中间有空格，用 `.includes('确')` 匹配）
5. [ ] 等待 3-6 秒生成
6. [ ] 点击顶部工具栏的 **橙色「保存」按钮**（右上角，不是 CKEditor 自己的保存！）
7. [ ] 点击 **「关闭」** → 弹窗「确定关闭吗？」→ **点「确 定」**（不能点弹窗的「关闭」按钮，否则无限堆叠！）
8. [ ] **验证：** `CKEDITOR.instances['ckeditor29'].getData().length > 100`

**备用方案（按钮点击无反应时）：**
```javascript
CKEDITOR.instances['ckeditor29'].setData(CKEDITOR.instances['ckeditor30'].getData());
// 仍需点「保存」使内容正式提交
```

**验证：** `ckeditor29` 的 textarea 应有内容（`CKEDITOR.instances['ckeditor29'].getData().length > 100`）

**注意事项：**
- 无线端描述不支持 GIF 格式图片
- 平台要求描述图片宽度大于 100px，不符合的自动移除
- 不写无线端描述时平台会自动抓取 PC 端内容截断，效果不好
- 详细操作见 `aliexpress-listing → references/wireless-description.md`

---

## Section G：包装信息

⚠️ **必须在 SKU 配置（Section E）填写完成后才填包装信息，数据必须一致！**

### G1 包装后重量
- [ ] **必须与 SKU 表中重量(kg)字段一致**（例：0.080）
- [ ] 1688 数据转换：45g → 0.045kg（用 kg 单位）
- [ ] 如果1688有含包装重量，优先用；否则用 SKU 表值加适量余量

### G2 包装后尺寸
- [ ] **必须与 SKU 表中长/宽/高一致**（例：6 × 3 × 2 cm）

---

## Section H：模版和其他设置

### H1 运费模板

⚠️ **别跟「---请选择引用模板---」搞混——一个在属性tab，一个在模版tab！**

- [ ] 在**模版信息** tab 中找到「请选择运费模板」下拉
- [ ] 根据 **零售价(¥) ÷ 7 ≈ 美金($)** 计算美金价
- [ ] 按价格区间选模板（详见 SKILL.md「运费模板选择标准」）：

| 零售价 | 美金 | 选此项 |
|:--|:--|:--|
| ~¥14-36 | $2-5 | 2-5美金 2kg以下 |
| ~¥36-58 | $5-8 | 5-8美金 2KG以下 |
| ~¥58-72 | $8-10 | 8-10美金 2KG以下 |
| ~¥72+ | ≥$10 | 10美金以上 2KG以下（或2kg以上） |

- [ ] 示例：¥55 ÷ 7 ≈ $7.9 → **5-8美金 2KG以下**

### H2 服务模板
- [ ] **只有一个选项**：Service Template for New Sellers
- [ ] 直接选中即可

### H3 海关监管属性
- [ ] 点击 **「添加海关监管」** 按钮（`button.ant-btn-primary`）
- [ ] 弹窗中选择品名(Product name)下拉
- [ ] **品名必须与产品标题保持一致**（如标题含"Necklace"→选"空气清新项链"；含"Air Purifier"→选"空气净化器"）
- [ ] ⚠️ 弹窗还包含「构造(Construction)」下拉，需选择一个值（通常选与产品相关的构造）
- [ ] ⚠️ 弹窗验证还包括：货值、重量、包装尺寸、是否选择——这些字段可能在弹窗内，也可能是独立的表单字段
- [ ] 点击 **「确定」** 关闭弹窗
- [ ] 验证：页面海关监管区显示已添加的监管属性条目

### H4 半托管服务
- [ ] **不参与**（不勾选）

### H5 报价是否含关税
- [ ] 选 **「不含关税报价」**

### H6 欧盟责任人
- [ ] **只有一个选项**，直接选中

### H7 品牌制造商
- [ ] 点开下拉
- [ ] 只有一个选项 → 直接选
- [ ] 有多个选项 → 选 **Shaoguan Jiuye Technology Co., Ltd**（韶关九野科技有限公司）

### H8 土耳其责任人
- [ ] **跳过，不选**

### H9 资质证件
- [ ] 暂时不填（用户后续提供）

---

## Section I：最终动作

### 保存
- [ ] 如果有验证错误无法「保存并移入待发布」→ 先点**「保存」**保留进度
- [ ] 修复所有错误后再点**「保存并移入待发布」**
- [ ] 保存后检查页面是否还有 `.ant-form-item-explain-error` 红色错误提示
- [ ] 页面刷新后标题字数显示正确（`您还可以输入N个字符`）

### 包装后尺寸填写（坑点）
- [ ] ⚠️ 尺寸必须填**整数**（6 不是 6.0） 
- [ ] 如果 nativeInputValueSetter 设了值仍报错「请填写整数」→ 用键盘输入方式：点击输入框 → Ctrl+A 全选 → Delete → 输入数字 → Tab 跳到下一个

### 通知用户
- [ ] 告诉用户「已保存到待发布，请检查」
- [ ] 列出已完成的条目和用户需要关注的条目
- [ ] 用户说OK后再点「发布」

---

## 常见坑（Pitfalls）

### ❌ 采集箱→待发布弹窗按钮「确 定」无法匹配（2026-06-16 发现）

**症状：** 从采集箱列表点「移入待发布」，弹窗出现，但 JavaScript 用 `=== '确定'` 匹配不到按钮。按钮文字实际是「确 定」（中间有空格），HTML 为 `<span>确</span><span>定</span>`。

**解决：**
```python
for (var b of document.querySelectorAll('.ant-modal button, .ant-btn-primary, button'))
    if (b.textContent.includes('确') && b.textContent.includes('定') && b.offsetParent) { b.click(); return; }
```

### ❌ 「保存」不持久化到服务端（2026-06-16 新发现）

**症状：** 用 Playwright 填完所有字段后点击顶部「保存」（简单保存）按钮，页面显示数据填好了（JS evaluate 确认），但回到采集箱列表一看——更新时间没变，标题还是中文，所有修改都没了。

**原因（推测）：** 店小秘编辑页的「保存」按钮可能依赖于特定的 React/Vue 事件系统，Playwright 的 JS click 虽然触发了按钮的 onclick handler，但没有经过框架的完整表单提交流程，导致数据只停留在客户端，没有 POST 到服务端。

**正确做法：**
1. **优先用路径 B（采集箱→移入待发布→再编辑→保存并移入待发布）**，不经过「保存」草稿步骤
2. **填完所有数据后直接点「保存并移入待发布」** —— 这个按钮走的是完整的表单验证+提交流程
3. 如果因为验证错误无法「保存并移入待发布」，**不要点「保存」期望存草稿**——改用路径 B 重新来

### ❌ 「保存并移入待发布」的已知验证错误（2026-06-16 发现）

以下错误在点击「保存并移入待发布」时触发，阻止发布：

| 错误信息 | 可能位置 | 修复 |
|:--|:--|:--|
| 请输入货值 | 海关监管属性弹窗 | 在海关监管弹窗中选品名后，还需填货值 |
| 请输入重量 | 海关监管属性弹窗 / 重量字段 | 每个SKU的货值/重量都要填 |
| 请完善包装尺寸 | 海关监管属性弹窗 / 包装信息tab | 填包装后尺寸（长×宽×高） |
| 请选择否是 | 海关监管属性弹窗 | 监管属性中的是否字段需要选择 |
| 请输入货值（重复） | 每个SKU变种 | 多SKU每个都要填货值 |
| 请输入重量（重复） | 每个SKU变种 | 多SKU每个都要填重量 |

**排查方法（点击保存并移入待发布后）：**
```python
# 收集所有可见的错误信息
errors = target.evaluate("""() => {
    var els = document.querySelectorAll('.ant-form-item-explain-error');
    return Array.from(els).filter(e => e.offsetParent).map(e => e.textContent.trim());
}""")
print(f"Validation errors: {errors}")
```

**症状：** 点击「保存并移入待发布」按钮，按钮可被点击（无报错），但页面不跳转、无成功/失败 toast、URL 不变、按钮依然可见。

**原因（已验证）：** 以下验证错误会导致保存**静默失败**，店小秘不显示任何错误提示！

| 错误类型 | 表现 | 解决 |
|:--|:--|:--|
| 标题含中文 | 页面顶部显示 对不起，您填写的标题中含有中文字符 | 删除所有中文字符，只保留英文+数字+空格 |
| 分类与速卖通推荐不匹配 | 页面顶部显示 当前产品选择分类和速卖通推荐分类有较大差距 | 换用速卖通推荐的分类 |
| 商品说明书未上传 | 表单字段下显示红色 请上传文件！ | 通过图片空间(PDF)方式上传说明书PDF |

**排查方法：** 在保存前先检查页面文本，检测阻塞因素：
```python
text = page.evaluate("() => document.body.innerText || ''")
if '中文字符' in text: print('⚠️ 标题含中文，需修复')
if '分类有较大差距' in text: print('⚠️ 分类不匹配，需修复')
```

**修复方法（标题含中文）：**
```python
page.evaluate("""() => {
    const inputs = document.querySelectorAll('input[placeholder*="标题"]');
    if (!inputs.length) return;
    const inp = inputs[0];
    let clean = (inp.value || '').replace(/[\\u4e00-\\u9fff]+/g, '').replace(/\\s+/g, ' ').trim();
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    setter.call(inp, clean.substring(0, 128));
    inp.dispatchEvent(new Event('input', {bubbles: true}));
    inp.dispatchEvent(new Event('change', {bubbles: true}));
}""")
```

### ❌ 商品说明书阻塞保存（2026-06-15 发现）
- 结果：点击「保存并移入待发布」按钮后，按钮可被点击且无页面级报错，但商品说明书字段显示红色错误「请上传文件！」
- 注意：此错误是**可见的**（非静默失败），保存失败后会停留在编辑页
- 解决：通过上传文件按钮 → 图片空间(PDF) → 选择已有PDF或本地上传 → 确定
- 如果暂时没有说明书PDF，可以先点「保存」（非强制校验）存草稿，下次再补

### ❌ 无线端描述弹窗堆叠无限循环
- 结果：点新版编辑器的「关闭」→ 弹出「确定关闭？」→ 又点「关闭」→ 越堆越多
- 解决：**正确顺序是**「保存」→ 「关闭」→ 确认弹窗点「确 定」→ 回到编辑页。确认窗弹出后**不能**继续点「关闭」，必须点「确 定」或「取 消」
- 紧急恢复：`document.querySelectorAll('.ant-modal-wrap').forEach(w => w.remove());`

### ❌ 标题含中文
- 结果：速卖通发布失败
- 解决：检查标题中每个字符，确保全英文

### ❌ 颜色值被废弃
- 结果：选了显示「该属性值平台已废弃，不支持选择！」
- 解决：选平台当前支持的颜色值（有些类目颜色限制不同）

### ❌ 零售价通过普通JS设置不生效
- 结果：React组件不响应 `input.value = '69.00'`
- 解决：使用 `nativeInputValueSetter` + 手动 dispatch input/change/blur 事件

### ❌ 属性下拉弹出但不显示选项
- 结果：dropdown DOM存在但 `display:none`
- 解决：用 Playwright `page.mouse.click(x, y)` 而非 evaluate click

### ❌ Ant Design Dropdown CDP 模式打不开（2026-06-15 发现）\n- 结果：Hermes browser 模式下，JS `.click()` 打不开 Ant Design Dropdown（React 事件绑定不走 JS 模拟点击）\n- 解决：使用 CDP `Input.dispatchMouseEvent` 鼠标事件坐标点击：\n  ```python\n  # 1. 获取元素坐标\n  coords = page.evaluate('''() => {{\n      var btn = document.querySelector(\".ant-select-selector\");\n      var r = btn.getBoundingClientRect();\n      return {{x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}};\n  }}''')\n  # 2. 用 CDP 鼠标事件点击\n  page._client.send('Input.dispatchMouseEvent', {\n      type: 'mousePressed', x: coords.x, y: coords.y, button: 'left', clickCount: 1\n  })\n  page._client.send('Input.dispatchMouseEvent', {\n      type: 'mouseReleased', x: coords.x, y: coords.y, button: 'left', clickCount: 1\n  })\n  ```\n- 适用于：所有 Ant Design Dropdown 组件（上传文件、Select 下拉、Dropdown Button 等）\n\n### ❌ browser_navigate 重载丢失未保存数据（2026-06-15 发现）\n- 结果：调用 `browser_navigate` 后页面从服务器重新加载，所有未保存的修改全部丢失（标题回中文、属性回「请选择」）\n- 原因：CDP 模式下 `browser_navigate` 等同于在 Chrome 地址栏输入 URL 回车，是全新的页面加载\n- 解决：\n  - 需要刷新页面时，先点「保存」存草稿\n  - 不要用 browser_navigate 刷新店小秘编辑页 — 用 JS 原地操作\n  - 如果页面卡死（文件上传阻塞等），先点「保存」再刷新
- 结果：颜色/SKU/价格等被重置
- 解决：全部填完后再保存，分段保存可能导致状态丢失

### ❌ 上传视频路径错误
- 结果：Playwright从WSL路径上传到Windows Chrome失败
- 解决：先把视频复制到 `/mnt/d/` 再用 `set_input_files(`/mnt/d/video.mp4`)`

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*