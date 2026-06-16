# PC端描述 — 引用模板操作

## 入口

编辑页左侧竖排 tab → 点「描述信息」（`.anchor-menu-item` 文本=「描述信息」）

### ⚠️ Tab 选择器注意

编辑页左侧的 tab 菜单是 **`div.anchor-menu-item`**（不是 `div.ant-tabs-tab`），包含以下 tab：
- 基本信息，店小秘信息，属性信息，产品信息，区域调价信息，**描述信息**，包装信息，模版信息，其他信息

**CDP 点击示例：**
```javascript
// 查找并点击「描述信息」tab
const items = document.querySelectorAll('div.anchor-menu-item, span, div, li, a');
for (const el of items) {
  if (el.innerText.trim() === '描述信息' && el.offsetParent !== null) {
    el.scrollIntoView({block: 'center'});
    el.click();
    break;
  }
}
```

## 引用模板操作序列

```
Step 1 → CKEditor 工具栏「引用模板」按钮（.cke_button__smttemplateprops）→ 弹窗
Step 2 → 弹窗三栏 tab：关联营销 / 自定义模板 / 尺码模板
Step 3 → 选中模板行 checkbox（<td class="f-left"> 中找模板名）
Step 4 → 点弹窗底部「选择」按钮（.ant-btn-primary，文本=「选择」）
Step 5 → 验证：CKEditor 中新增 <img data-kse="...relatedProduct...">
```

## PC端描述 — 批量改图片尺寸（用户2026-07-18验证的完整7步序列）

### 重大陷阱：两个「批量编辑图片」按钮

CKEditor 工具栏**有两个同名「批量编辑图片」元素**：

| 按钮 | 位置 | 类 | 结果 |
|:--|:--|:--|:--|
| CKEditor combo | 工具栏左侧 | `.cke_combo__batcheditimgdropdownlist` | 空面板 ❌ |
| images-options | 展开图片栏后下方 | `.images-options .ant-dropdown-trigger` | 正确菜单 ✅ |

### 前置：展开图片栏

CKEditor 工具栏最右侧「展开图片栏」（`.cke_button__imagepaneltoggle`）默认收起。
必须先点它展开。

触发方式：
```javascript
var btn = document.querySelector('.cke_button__imagepaneltoggle');
btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
btn.dispatchEvent(new MouseEvent('click', {bubbles: true}));
```

### 展开后结构

```
CKEditor 工具栏: [选择图片▼] [批量编辑图片▼] [引用模板] [AI生成] [展开图片栏]
图片列表: 790x1017 790x1016 790x1017 ...
options: [批量编辑图片 ▼]  [添加水印]  [crop编辑图片]
                                          ↑ 目标按钮
```

### ⭐ 完整7步操作序列（用户2026-07-18验证）

**铁律：严格按顺序，每步做完让用户确认看到变化再走下一步。不许跳步，不许猜下一步。**

1. **滚动到合适位置：** 把按钮滚到视口 y≈400-700（`scrollBy(0, r.top-400)`），预留下拉空间
2. **点开下拉：** `Input.dispatchMouseEvent(mousePressed+mouseReleased)` 在按钮坐标上触发（JS `.click()` 对 antd 无效）
3. **选「批量改图片尺寸」：** `.ant-dropdown-menu-item` textContent 匹配
4. **改「自定义比例调整」：** 用 `Input.dispatchMouseEvent` 点 `.ant-select-selector` 坐标 → 下拉出现 → 点「自定义比例调整」
5. **图片宽填800：** `input[name=valueW]` 设 value='800'（nativeValueSetter + dispatchEvent）
6. **选择全部：** 点 `.ant-checkbox-wrapper` textContent 含「选择全部」的 label
7. **生成JPG图片：** 点 button textContent 含「生成JPG」

### 关键技术细节

- **CDP鼠标事件（antd唯一有效方式）：** JS `.click()` 对 antd 无效。必须用 `Input.dispatchMouseEvent(type='mousePressed', x, y)` + `(type='mouseReleased', x, y)` 在按钮实际坐标触发。
- **滚动防止偏移：** 按钮在视口底部时，antd 将 dropdown 渲染在绝对坐标 top: 5612px（视口外）。检测：`display:'block'` 但 `rect` 全零 → 在视口外 → scroll 重试。
- **ant-select-selector 同理：** 弹窗内下拉选择器同样需要坐标级 mousePressed+mouseReleased。
- **默认「等比例调整」必须改成「自定义比例调整」。** 否则没有完整宽高输入。
- **「选择全部」不是默认勾选，需要主动点击。**

### 与产品主图改尺寸的区别

| 对比项 | 产品主图 | PC端描述 |
|:--|:--|:--|
| 入口 | 「编辑图片」按钮（产品图片区） | 「批量编辑图片」（images-options区） |
| 前置条件 | 无 | 必须先展开图片栏 |
| 下拉数量 | 2个 | 3个 |
| 宽高输入 | 宽+高两个输入框 | 一个px输入框 |

## PC端描述 — 图片翻译操作流程

### 入口

与「批量改图片尺寸」**同一个入口**：展开图片栏 → `.images-options .ant-dropdown-trigger`（批量编辑图片）。

### 弹窗 UI 结构

```
┌─ 图片翻译 ──────────────────────────────────────────────┐
│ [✓] 选择全部         [✓] 快速翻译                        │
│ 1、按张(次)收费...                                       │
│ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
│ │img 0│ │img 1│ │ ... │ │ ... │ │ ... │ │ ... │      │
│ │[✓]  │ │[✓]  │ │[ ]  │ │[ ]  │ │[ ]  │ │[ ]  │      │
│ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘      │
│                                    [一键翻译]  [关闭]   │
└──────────────────────────────────────────────────────────┘
```

- **「选择全部」** = 全选所有图片的 checkbox（默认未勾选）
- **「快速翻译」** = 翻译模式 toggle checkbox（**默认已勾选**），不是操作按钮。翻译前确认它是勾选状态即可，不要点它。
- **「一键翻译」** = 实际提交翻译的操作按钮（`.ant-btn-primary`，文本="一键翻译"）
- **「关闭」** = 关闭弹窗
- 每张图片下方有个 `.image-checkbox`（`.ant-checkbox-wrapper`）逐个勾选

### 完整操作序列

1. **展开图片栏**（如未展开）：点 CKEditor 工具栏 `cke_button__imagepaneltoggle`
2. **点开「批量编辑图片」dropdown**：`Input.dispatchMouseEvent(mousePressed+mouseReleased)` 在 `.images-options .ant-dropdown-trigger` 坐标触发
3. **选择「图片翻译」**：在 `.ant-dropdown-menu` 中点 textContent 匹配「图片翻译」的菜单项
4. **弹窗出现**：`ant-modal` title="图片翻译"，body 含 22 张图片（前 6 张 800×800 产品主图，后 16 张 800×1030 PC 描述图）
5. **取消「选择全部」**：弹窗中 `.ant-checkbox-wrapper` textContent 含「选择全部」→ 若已勾选则点击取消
6. **只选择有中文文案的图片**：逐张 OCR 判断 → 点对应 `.image-checkbox` 使 `.ant-checkbox-input.checked=true`
7. **确认「快速翻译」已勾选**（默认已勾选，不要动它），然后**点击「一键翻译」按钮**
8. **验证结果：** 点击后弹窗继续打开（不会自动关闭），可检查图片是否已变成英文。如果提示「投递失败」说明翻译服务可能暂无额度或图片已翻译过，**不要反复点击**

### 图片中文字检测方法对比

#### 方法 A：pytesseract + chi_sim+eng（推荐 ✅）

比 ddddocr 识别准确率高，能输出实际中文内容供判断：

```python
import pytesseract
from PIL import Image

# 下载图片到本地
import urllib.request
for i, url in enumerate(img_urls):
    urllib.request.urlretrieve(url, f'/tmp/translate_imgs/img_{i}.jpg')

# OCR 检测
for i in range(len(img_urls)):
    img = Image.open(f'/tmp/translate_imgs/img_{i}.jpg')
    text = pytesseract.image_to_string(img, lang='chi_sim+eng', config='--psm 6')
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
```

#### 方法 B：ddddocr（备选）

当 pytesseract 不可用时使用：

```python
import ddddocr
ocr = ddddocr.DdddOcr(beta=True)
for i in range(len(img_urls)):
    with open(f'/tmp/translate_imgs/img_{i}.jpg', 'rb') as f:
        text = ocr.classification(f.read())
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in text)
```

#### 两种方法对比

| 特性 | pytesseract+chi_sim | ddddocr |
|:--|:--|:--|
| 输出内容 | 完整句子/段落 | 单个字符 |
| 假阳性 | 低（大段英文噪声但罕见误判为中文） | 高（噪点/水印被识别为「认」「业」「一」「口」等单字） |
| 安装依赖 | `tesseract-ocr-chi-sim` + `pytesseract` | `ddddocr` |
| 批量速度 | 约 1-2s/图 | 约 0.5s/图 |

**⚠️ 最佳实践：** 用 pytesseract 检测后，将检测到的中文内容（如「外出不怕喝水难」「硅胶材质无毒无异味」「参数信息」）随索引号一并报告给用户。用户目视对比屏幕确认。不要仅凭 OCR 做最终决定。

### 图片中文字检测（vision API 不可用时的替代方案）

当辅助视觉 API 断开或不支持界面识别时，用 ddddocr 离线检测每张图片是否含中文：

```python
# Step 1: 从页面获取所有图片 URL
img_urls = await page.evaluate("""() => {
    const modal = document.querySelectorAll('.ant-modal')[3];  // 索引3=图片翻译弹窗
    return Array.from(modal.querySelectorAll('img')).map(img => img.src);
}""")

# Step 2: 下载图片
import urllib.request
for i, url in enumerate(img_urls):
    urllib.request.urlretrieve(url, f'/tmp/translate_imgs/img_{i}.jpg')

# Step 3: OCR 检测
import ddddocr
ocr = ddddocr.DdddOcr(beta=True)
for i in range(len(img_urls)):
    with open(f'/tmp/translate_imgs/img_{i}.jpg', 'rb') as f:
        text = ocr.classification(f.read())
    has_chinese = any('\\u4e00' <= c <= '\\u9fff' or '\\u3400' <= c <= '\\u4dbf' for c in text)
```

**⚠️ 已知限制：** ddddocr 可能将噪点/图案误识别为单个汉字（如「认」「业」「一」「口」），导致假阳性。**最佳做法：** 报告检测结果 + 建议用户从屏幕目视确认，用户有最终决定权。

### 关键陷阱

| 陷阱 | 说明 | 解决方案 |
|:--|:--|:--|
| 图片索引与屏幕布局 | 22 张图：索引 0-5 为产品主图（800×800），6-21 为 PC 描述模板图（800×1030/1029） | 用 OCR 检测后报告索引号，方便用户对照屏幕 |
| 先取消再选 | 默认「选择全部」已勾选，用户要**先取消再单个选** | 顺序：取消选择全部 → 清空所有 image-checkbox → 只勾指定的 |
| OCR 假阳性 | 纯装饰性线条/水印可能被检测出「中文」 | 报告检测文字内容供用户判断，不自行决定 |
| 收费提示 | 弹窗注「按张收费，即使无文字也扣费」 | 不要全选无中文的图片，避免浪费配额 |

## 代码实现速查

```python
import asyncio

# Step 1: 滚动到合适位置
await page.evaluate('window.scrollTo(0, 4180)')
await asyncio.sleep(0.5)

# 获取按钮坐标
coords = await page.evaluate('''() => {
    const r = document.querySelector('.images-options .ant-dropdown-trigger').getBoundingClientRect();
    return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
}''')

# 按钮移到视口中部
if coords['y'] > 700:
    await page.evaluate(f'window.scrollBy(0, {coords["y"] - 400})')
    await asyncio.sleep(0.5)
    # 重新获取坐标
    coords = await page.evaluate('''() => {
        const r = document.querySelector('.images-options .ant-dropdown-trigger').getBoundingClientRect();
        return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
    }''')

# Step 2: Input.dispatchMouseEvent 真实点击
await page.evaluate('''() => { /* placeholder - use CDP Input */ }''')
# 实际执行：browser_cdp Input.dispatchMouseEvent
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*