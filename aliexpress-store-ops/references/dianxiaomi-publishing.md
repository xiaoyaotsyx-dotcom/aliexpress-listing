# 店小秘 1688→AliExpress 商品发布工作流

> 本文件记录 [你的店铺名称] 从 1688 采集到店小秘编辑再到速卖通发布的完整流程和发现。

## 用户设备信息
- Windows 用户名: [你的Windows用户名]
- 店小秘账号: [你的店铺名称] (卖家名称: [你的店小秘用户名])
- 速卖通店铺: [你的店铺名称]
- 速卖通后台 channelId: 2358619

## 店小秘页面URL速查
- 编辑页: `https://www.dianxiaomi.com/web/smt/edit?id={product_id}`
- 在线产品列表: `https://www.dianxiaomi.com/web/smt/smtProductList/online`
- 采集箱: `https://www.dianxiaomi.com/web/smt/smtProductList/collect`

## 产品分类路径（已验证）
| 品类 | 4级路径 |
|:--|:--|
| 空气净化器（挂脖） | 家用电器(Home Appliances) > 生活家电(Household Appliances) > 空气处理小家电(Small Air Conditioning Appliances) > 空气净化器(Air Purifiers) |
| 冰贴 | 家居用品(Home & Garden) > 家居日用品(Household Merchandises) > 扇/迷你风扇/配件/冰垫/冰贴(Cooling Products) > 冰贴(Ice Stickers) |

## 参考产品法（用户明确的工作方式）
1. 用户打开一个已上架的成熟产品（在店小秘编辑页）
2. Agent 提取该产品的标题结构、属性选择、SKU配置、图片组织、定价策略
3. Agent 将提取的模式应用到新产品
4. 品类差异导致的属性不同则按产品实际情况调整
5. 不确定时问用户

## 店小秘编辑页 tab 结构
1. **基本信息** — 店铺名、标题（128字符英文无中文）、分类（4级）
2. **店小秘信息** — 来源URL（1688链接，仅内部生效）
3. **属性信息** — 品牌/电压/产地/功率/噪音/功能/认证/电源/风速等。属性选项由AliExpress动态加载，从选项中选择
4. **产品信息** — 产品分组、图片（主图最多6张）、营销图（1:1白底+3:4场景）、视频、计件单位、销售方式
5. **区域调价信息** — 按比例对特定国家加减价
6. **描述信息** — HTML详情
7. **包装信息** — 包装尺寸/重量
8. **模版信息** — 运费/服务模版
9. **其他信息** — 产品有效期（实际统一5年）

## SKU 配置
- Color variant: `颜色` + `自定义名称` + `图片` + `零售价` + `货值` + `库存` + `重量(kg)` + `包装尺寸(cm)` + `商品编码`
- 批发价：件/个以上减免 %
- 物流属性按SKU选择（`非纽扣锂离子电池`等）
- 商品编码可一键生成
- 详见 `references/sku-variant-config.md`

## 产品图片编辑
产品图片的尺寸调整和编辑流程详见 `references/dianxiaomi-image-editing.md`
- ⚠️ 关键：必须同时设两个下拉（自定义比例调整 + 自定义宽高）才能得到精确800×800
- 品牌必须选（可选 NONE(无品牌)）
- 新商品不填发货期（平台默认7天）
- 分类与速卖通推荐差距大时提示修改
- SPA 导航要点：React 菜单无 href，需展开后找隐藏子菜单链接，然后直接 goto
- 用户偏好：先填完→保存→通知检查→用户确认后再发布。不发布

## 品类属性索引参考（空气净化器）
见 `references/air-purifier-attribute-map.md`

## Ant Design Select 交互要点
- 下拉框 portal 渲染到 body 层，初始 `display:none`
- 必须用 Playwright 原生 `page.mouse.click()` 触发真实的 mousedown+click 事件
- 用 `page.evaluate` 内的 `item.click()` 选择选项
- 每次选择后页面可能重新渲染导致索引变化
- 属性值可能不匹配（1688中文 vs AliExpress英文选项），选最接近的

## 图片编辑
产品图片的尺寸调整和编辑流程详见 `references/dianxiaomi-image-editing.md`

## 媒体资源获取
1688 视频/图片的提取和上传详见 `references/media-sourcing.md`

## React 表单字段赋值
使用 `Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set` + 手动 dispatch input/change 事件

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*