# 店小秘编辑页 Tab 导航

> 店小秘编辑页使用 Ant Design Tabs 组件。可通过两种方式切换 tab：
> 1. DOM 元素点击（推荐 — 保持页面状态）
> 2. URL hash 修改（快速跳转，但可能丢失部分状态）

## 方式一：DOM 元素点击（推荐）

通过查找页面上 tab 文字并点击：

```python
def navigate_to_tab(page, tab_name):
    page.evaluate('(tb) => {\n'
        'const all = document.querySelectorAll("*");\n'
        'for (const el of all) {\n'
        '  if (el.textContent && el.textContent.trim() === tb && el.offsetParent !== null) {\n'
        '    el.click(); return;\n'
        '  }\n'
        '}\n'
        '}', tab_name)

# 使用
navigate_to_tab(page, '属性信息')
navigate_to_tab(page, '模版信息')
navigate_to_tab(page, '包装信息')
navigate_to_tab(page, '基本信息')
navigate_to_tab(page, '描述信息')
```

## 方式二：URL hash

编辑页 URL 支持 hash 锚点直接跳转 tab。**注意：** 修改 hash 后需要 `time.sleep(2)` 等待 React 渲染。

```python
# 直接导航到 tab
hashes = {
    '基本信息':     '#productBasicInfo',
    '店小秘信息':   '#productStoreInfo',
    '属性信息':     '#productAttributeInfo',
    '产品信息':     '#productProductInfo',
    '区域调价信息': '#productAreaPrice',
    '描述信息':     '#productDescription',
    '包装信息':     '#productPackInfo',
    '模版信息':     '#productTemplateInfo',
    '其他信息':     '#productOtherInfo',
}

def goto_tab_by_hash(page, tab_name):
    if tab_name in hashes:
        page.evaluate(f"() => window.location.hash = '{hashes[tab_name]}'")
        time.sleep(2)
```

### 已知 hash 值

| Tab 名称 | URL Hash | 字段 |
|:--|:--|:--|
| 基本信息 | `#productBasicInfo` | 标题、分类、SKU配置 |
| 店小秘信息 | `#productStoreInfo` | 来源URL |
| 属性信息 | `#productAttributeInfo` | 品牌/电压/产地等产品属性 |
| 产品信息 | `#productProductInfo` | 图片、视频、分组 |
| 区域调价信息 | `#productAreaPrice` | 按国家调价 |
| 描述信息 | `#productDescription` | PC端+无线端描述 |
| 包装信息 | `#productPackInfo` | 包装后重量/尺寸 |
| 模版信息 | `#productTemplateInfo` | 运费/服务/海关/欧盟/品牌制造商 |
| 其他信息 | `#productOtherInfo` | 产品有效期 |

## 注意事项

- 修改 hash 后需等待 React 重新渲染（2-3 秒）
- 部分 tab（如属性信息）的内容可能在 hash 跳转后不完全渲染，需要额外的 `page.evaluate` 滚动触发
- Ant Design Select 下拉在 CDP 模式下必须用 `page.mouse.click` 坐标点击才能展开，JS `.click()` 无效
- 点击 tab 后不要立即操作下拉，给 `time.sleep(2)` 让 React 渲染选项

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*