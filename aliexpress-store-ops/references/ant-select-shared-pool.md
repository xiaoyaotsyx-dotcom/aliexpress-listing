# Ant Design Select 共享下拉池 — CDP 模式操作指南

> 2026-06-11 发现于店小秘编辑页（速卖通产品属性区域）
> 适用所有使用 Ant Design Select `showSearch` 的页面

## 问题现象

在通过 Playwright CDP (`connect_over_cdp`) 操作店小秘编辑页时，点击任一属性下拉框，dropdown 面板中显示的是**所有属性的全部选项**（品牌/噪音/风量等混在一起），而非仅当前属性的选项。

**典型表现：**
- 点「品牌」下拉 → 看到 NONE(NONE)、≤50分贝、50立方米/小时等选项混在一起
- 点「噪音」下拉 → 同样看到品牌、噪音、风量等选项全部混在一起
- 点「风量」下拉 → 同样

## 根本原因

Ant Design Select 的 dropdown 通过 Portal 渲染到 `<body>` 尾部，但 CDP 模式下**所有选择的选项数据共享同一个虚拟滚动列表实例**。每个 Select 只负责控制自己当前的选中值，下拉面板的选项渲染由全局状态管理。

这意味着：
- 所有 Select 的选项池共享，打开任意一个都看到全部
- 搜索输入框（`input[type="search"]`）会过滤到这个共享池
- 直接 `select_option()` 可能选到错误属性的选项

## 操作模式的演进

先后尝试过三种方案：

### 方案A（已废弃 + 用户禁令）：搜索过滤法

**用户明确禁止在搜索框中输入关键词来过滤选项**（2026-07-03 指令）。即使技术可行也不得使用。

技术上 `nativeSetter` + `dispatchEvent('input')` 在 CDP 模式下也不生效。 Ant Design Select 的 `onSearch` 回调依赖于 React 合成事件，而 `nativeSetter` + `dispatchEvent` 虽然冒泡到 DOM，但 React 的 Fiber 调度器不识别这种方式触发的 `input` 事件。因此搜索输入框不会过滤选项，所有属性选项混在一起保持可见。-03 指令）。即使技术可行也不得使用。

技术上 `nativeSetter` + `dispatchEvent('input')` 在 CDP 模式下也不生效。 Ant Design Select 的 `onSearch` 回调依赖于 React 合成事件，而 `nativeSetter` + `dispatchEvent` 虽然冒泡到 DOM，但 React 的 Fiber 调度器不识别这种方式触发的 `input` 事件。因此搜索输入框不会过滤选项，所有属性选项混在一起保持可见。

### 方案B（推荐）：click + scroll 模式

正确的方式是：**只打开下拉、不进行搜索过滤、在可见选项中找到匹配项直接 click()。**

```python
def select_ant_option(page, label_text, option_text):
    \"\"\"
    通过标签名找到属性下拉，打开后从可见选项中选择目标选项。
    不进行搜索过滤——nativeSetter + dispatchEvent 在 CDP 下不触发 React onSearch。
    
    Args:
        page: Playwright Page 对象
        label_text: 属性标签文字，如 '品牌', '噪音', '风量'
        option_text: 选项包含的文字，用于匹配
    \"\"\"
    # 1. 找到 Select selector 的 mouse.click 坐标
    pos = page.evaluate(f\"\"\"(t) => {{
        const items = document.querySelectorAll('.ant-form-item');
        for (const item of items) {{
            const label = item.querySelector('.ant-form-item-label label');
            if (label && label.textContent.includes(t)) {{
                const sel = item.querySelector('.ant-select-selector');
                if (sel) {{
                    sel.scrollIntoView({{block: 'center'}});
                    const r = sel.getBoundingClientRect();
                    return {{x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}};
                }}
            }}
        }}
        return null;
    }}\"\"\", label_text)
    if not pos: return False
    time.sleep(0.3)
    page.mouse.click(pos['x'], pos['y'])
    time.sleep(2)  # 等待 portal 渲染
    
    # 2. 从可见选项中选择（不搜索过滤！）
    result = page.evaluate(f\"\"\"(o) => {{
        const dds = document.querySelectorAll('.ant-select-dropdown');
        for (const dd of dds) {{
            if (dd.offsetParent !== null) {{
                const items = dd.querySelectorAll('.ant-select-item-option');
                for (const item of items) {{
                    const text = item.innerText.trim();
                    if (text.includes(o)) {{
                        item.click();
                        return 'OK: ' + text;
                    }}
                }}
                // 如果没找到，可能选项在虚拟滚动未渲染区域
                // 尝试用 ArrowDown 滚动
                for (let i = 0; i < 30; i++) {{
                    const evt = new KeyboardEvent('keydown', {{key: 'ArrowDown', bubbles: true}});
                    document.activeElement?.dispatchEvent(evt);
                }}
                // 重新查找
                const items2 = dd.querySelectorAll('.ant-select-item-option');
                for (const item of items2) {{
                    const text = item.innerText.trim();
                    if (text.includes(o)) {{
                        item.click();
                        return 'OK(scrolled): ' + text;
                    }}
                }}
                return 'not found in visible: ' + o;
            }}
        }}
        return 'no visible dropdown';
    }}\"\"\", option_text)
    
    print(f\"  {label_text}: {result}\")
    time.sleep(1)
    return 'OK' in result
```

## 常见属性搜索词速查

| 属性 | 推荐 filter_text | 推荐 option_text | 说明 |
|:--|:--|:--|:--|
| 品牌(Brand Name) | `NONE` | `NONE(NONE)` | 无品牌产品 |
| 噪音(Noise) | `35` 或 `30` | `≤35分贝` 或 `≤30分贝` | 1688说36dB以下，选最接近的 |
| 风量(Air Volume) | `50` | `50立方米` | 1688的50m³/h |
| 电压(Voltage) | `5` | `5V(5V)` | USB设备 |
| 产地(Origin) | `中国` | `中国大陆` | 通常选中国大陆 |
| 功率(Power) | `1` | `1瓦(1w)` | 低功耗设备 |
| HEPA滤网等级 | `其他` | `其他(Other)` | 无HEPA的产品 |
| 功能(Function) | `净化` | `净化空气` | 空气净化器 |
| 安装方式(Installation) | `便携` 或 `不需` | `便携式` 或 `不需安装` | 挂脖产品 |
| 电源(Power Source) | `USB` | `USB(USB)` | USB供电 |

## 与非搜索 Select 的区别

部分属性（如「电源(Power Source)」）的选项是直接平铺在页面上的 radio-style 选择（多个 span 可多选/单选），不是下拉搜索模式。这些不需要搜索过滤，直接 `click()` 对应 span 即可。

判断方法：看选项是 `ant-select` 组件还是 `span + input[type=checkbox]` 组合。

---

### ⚠️ 共享池腐败（2026-06-16）

详见 `ant-select-shared-pool-corruption.md`：经过多次操作后，共享池内部状态会永久腐败，电压和功率属性完全无法设置值。唯一修复方法是新开编辑页。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*