---
name: dxm-other-info
description: 店小秘速卖通编辑页——其他信息模块：半托管/关税/责任人/制造商/资质 + 区域调价 + 保存并移入待发布
domain: ecommerce
triggers:
  - 用户说"其他信息"、"欧盟责任人"、"区域调价"、"保存"、"发布"
---

# 店小秘其他信息模块

## 位置

单页面布局，#otherInfo section 在 y≈8853，#adjustPriceInfo 在 y≈4215。

## 字段

| 字段 | 类型 | 操作 | 星号 |
|:--|:--|:--|:--|
| 半托管服务 | checkbox | 默认参与(已勾选) | |
| 报价是否含关税 | radio | 不含关税(1)/含关税(2)，默认1 | ⭐ |
| 欧盟责任人 | select | 选预设或跳过 | |
| 土耳其责任人 | select | 通常跳过 | |
| 品牌制造商 | select | 选预设或跳过 | |
| 商机品关联 | 按钮 | 跳过 | |
| 资质信息 | 上传 | 跳过 | |

## 操作规则

- **半托管服务**：跳过不碰（用户2026-07-19指令）
- **报价是否含关税** ⭐：点击「不含关税报价」radio（不是默认已选，需要主动点击）
- **欧盟责任人**：只有一个选项，选那个（MJCM SARL）。JS `selector.click()` + `item.click()` 有效
- **土耳其责任人**：跳过
- **品牌制造商**：只有一个选项，选那个（Shaoguan Jiuye Technology Co., Ltd）。**必须用 keyboard Enter 选**：Playwright `elem.click()` 开下拉 → `page.keyboard.press('Enter')` 选中。JS `.click()` 对品牌制造商无效（Vue不响应）
- **商机品关联**：跳过
- **资质信息**：跳过
- **区域调价信息**：跳过

## 保存并移入待发布

### 🔴 铁律
所有模块填完→QA检查通过→用户说OK→才点保存！绝不自行发布！

### 按钮
页面顶部右侧「保存并移入待发布」

### 操作
```python
await page.evaluate('''() => {
    window.scrollTo(0, 0);
}''')
await asyncio.sleep(0.5)

# JS点保存
await page.evaluate('''() => {
    const btns = document.querySelectorAll('button');
    for (const btn of btns) {
        if (btn.textContent.includes('保存并移入待发布')) {
            btn.click();
            break;
        }
    }
}''')
```

### ⚠️ 注意
- 保存后等3-5秒检查提示消息
- 移入待发布弹窗「确 定」有空格
- 不依赖「保存」按钮存草稿——那不可靠

## ⚠️ 已知坑点
1. all sections on one page——scrollTo 跳转，不是独立tab页
2. 保存按钮在顶部，需scrollTo(0,0)才能看到
3. 其他信息大多默认正确，主要检查关税和保存
4. **品牌制造商keyboard Enter可能误触品牌字段（2026-07-19）：** 品牌和品牌制造商在同一视口区域。填完品牌制造商后必须验证品牌字段仍为NONE。如被覆盖，重新打开品牌下拉选NONE。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*