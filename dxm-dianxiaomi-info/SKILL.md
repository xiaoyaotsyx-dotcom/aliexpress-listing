---
name: dxm-dianxiaomi-info
description: 店小秘速卖通编辑页——店小秘信息模块：来源URL（只读，记录用）
domain: ecommerce
triggers:
  - 用户说"店小秘信息"、"来源URL"
---

# 店小秘店小秘信息模块

## 功能
此模块仅有一个字段：**来源URL**，显示的是采集自1688的原始链接。

## 操作
- 只读，无需修改
- 「访问」按钮可在新标签页打开1688源页面（**必须开新标签页，不能覆盖编辑页！**）

## 获取URL
```
Runtime.evaluate:
  const links = document.querySelectorAll('a');
  for (const l of links) {
    if (l.href && l.href.includes('detail.1688.com')) return l.href;
  }
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*