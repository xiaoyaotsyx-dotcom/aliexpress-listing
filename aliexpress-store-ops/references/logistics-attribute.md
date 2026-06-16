# 店小秘 物流属性（电池类）配置

> 适用于速卖通商品发布时的物流属性批量设置。挂脖空气净化器/迷你风扇等USB充电便携设备的内置电池选择。

## 常见产品的电池选择

| 产品类型 | 选择路径 | 原因 |
|:--|:--|:--|
| 挂脖空气净化器（USB充电） | 内电 > 非纽扣锂离子电池 | 内置可充电锂离子电池，非纽扣型 |
| 迷你风扇（USB充电） | 内电 > 非纽扣锂离子电池 | 同上 |
| 蓝牙耳机（充电盒） | 内电 > 充电盒式蓝牙耳机 | 专用选项 |
| 纽扣电池产品 | 内电 > 纽扣式锂电池 | 如CR2032等 |

## 弹窗全部选项树

弹窗打开后，可选的物流属性类别：

- 禁运 > 禁运
- 普货 > 普货
- 纯电 > 纯电
- 强磁 > 强磁
- 特货 > 液体粉末膏体 / 特货其他
- 特敏 > 危险品 / 特敏其他
- **内电** > 干电池 / 铅酸蓄电池 / 镍氢电池 / 其他电池 / 纽扣式锂电池 / 非纽扣锂金属电池 / 充电盒式蓝牙耳机 / **非纽扣锂离子电池**
- 外电 > 外电
- 弱磁 > 弱磁

## 1688产品电池信息提取

1688产品页通常不会明确写「电池类型」，但可以通过以下线索判断：

1. **查看产品参数** — 搜索「电源方式」字段：`USB` → 有内置充电锂电池
2. **查看功能亮点** — 关键词 `USB便捷充电`、`USB充电` 表示内置可充电电池
3. **物理规格** — 小尺寸（6×3×2cm）+ 轻重量（45g）→ 小型聚合物锂电池
4. **搜索关键词** — 在页面文本中搜索：`电池`、`充电`、`内置`、`锂`、`mAh`

**判断逻辑：**
- USB充电 + 便携/挂脖 + 轻量 → **非纽扣锂离子电池**
- 如果是纽扣电池仓/CR电池 → **纽扣式锂电池**
- 如果是干电池仓（AA/AAA）→ **干电池**
- 不确定时选 **非纽扣锂离子电池**（最通用的内置可充电电池选项）

## 操作代码

```python
import time

# 1. 点 (批量) 链接
page.evaluate("""
    () => {
        const cells = document.querySelectorAll('th, td');
        for (const cell of cells) {
            const text = cell.textContent || '';
            if (text.includes('物流属性') && text.includes('批量')) {
                const link = cell.querySelector('span.link');
                if (link) link.click();
                return;
            }
        }
    }
""")
time.sleep(2.5)

# 2. 在弹窗中选择电池类型
page.evaluate("""
    () => {
        const modal = document.querySelector('.ant-modal');
        if (!modal) return;
        const all = modal.querySelectorAll('*');
        for (const el of all) {
            if (el.textContent?.trim() === '非纽扣锂离子电池') {
                el.click();
                return;
            }
        }
    }
""")
time.sleep(1.5)

# 3. 点确定
page.evaluate("""
    () => {
        const btns = document.querySelectorAll('button');
        for (const btn of btns) {
            if (btn.textContent?.trim() === '确定') {
                btn.click();
                return;
            }
        }
    }
""")
```

## 验证

设置后，检查 SKU 表每行的物流属性列是否显示了对应的电池名：

```python
text = page.evaluate("() => document.body.innerText")
lines = text.split('\n')
# 应看到每行有「非纽扣锂离子电池」字样
battery_lines = [(i, l) for i, l in enumerate(lines) if '非纽扣锂离子' in l]
# 例：[(417, '非纽扣锂离子电池'), (431, '非纽扣锂离子电池'), (445, '非纽扣锂离子电池')]
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*