# Playwright CDP 连接 — 店小秘操作指南

## 为什么用 Playwright 而不是 Hermes 自带 browser 工具

| 场景 | Hermes browser 工具 | Playwright |
|:--|:--:|:--:|
| 普通点击/填表 | ✅ | ✅ |
| Ant Design Select 下拉 | ⚠️ 需坐标点击 | ✅ 更稳定 |
| Ant Design Dropdown 菜单 | ❌ click 无效 | ✅ expect_file_chooser |
| 文件上传 (file input) | ❌ DOM.setFileInputFiles 静默失败 | ✅ file_chooser.set_files |
| CKEditor 内容编辑 | ⚠️ 需 JS evaluate | ✅ 一致 |
| 页面快照/截图 | ✅ | ✅ |

**优先用 Hermes browser 工具**做常规操作，遇到文件上传或 Ant Design 下拉打不开时降级到 Playwright。

## 连接方式

```python
from playwright.sync_api import sync_playwright

# ⚠️ 用 HTTP URL，不是 WebSocket URL！
browser = sync_playwright().chromium.connect_over_cdp('http://127.0.0.1:19223')
```

- `http://127.0.0.1:19223` — 通过 WSL Python 中继
- `http://localhost:19223` — 等同

## 查找编辑页

```python
page = None
for ctx in browser.contexts:
    for pg in ctx.pages:
        if 'smt/edit' in pg.url and 'devtools' not in pg.url:
            page = pg; break
    if page: break

if not page:
    page = browser.contexts[0].new_page()
    page.goto(f'https://www.dianxiaomi.com/web/smt/edit?id={product_id}')
```

## 注意事项

1. **页面刷新数据会丢** — 店小秘编辑页用 Vue 3，`browser_navigate` 或页面重载会丢失所有未保存数据
2. **文件路径用 Linux 格式** — WSL 环境用 `/mnt/c/Users/...`，不要用 `C:\...`
3. **用完释放** — Playwright 脚本结束后自动释放，不需要手动 kill

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*