# 1688 参数提取实战记录（2026-06-14） 

## 提取方法

### 路径1：window.context JSON（主路径）

```js
// 在1688页面 Runtime.evaluate
const scripts = document.querySelectorAll('script');
let json = '';
for (const s of scripts) {
  if (s.textContent.includes('window.context')) {
    json = s.textContent;
    break;
  }
}
// 提取 productPackInfo
const m = json.match(/productPackInfo[^}]*weight[^}]*}/);
```

### 路径2：页面文本（辅助路径）

```js
const text = document.body.innerText;
// 从 "材质" 开始截取500字符
const start = text.indexOf('材质');
const slice = text.substring(start, start + 500);
```

## 实战案例：折叠喝水神器

### 提取结果

| 参数 | 值 | 来源 |
|------|-----|------|
| 材质 | 硅胶 | 页面文本 |
| 品牌 | 斌凯 | 页面文本 |
| 产地 | 义乌 | 页面文本 |
| 货号 | BK | 页面文本 |
| 重量 | 200g (0.2kg) | window.context → productPackInfo |
| 价格 | ¥1.30 | 页面文本 |
| 库存 | 绿714415 / 粉741140 | 页面文本 |
| 规格 | 宠物户外喂水碗【绿色】/【粉色】 | window.context |
| 箱装数量 | 120 | 页面文本 |

### window.context 关键路径

```
window.context.result.data.productPackInfo.fields.pieceWeightScale.pieceWeightScaleInfo[]
  └── [{sku1: "宠物户外喂水碗【绿色】", weight: 200, skuId: ...}, ...]
```

### 页面文本关键区域

```
材质\n硅胶\n成套自动喂食\n否\n品牌\t斌凯\n产地\t义乌\n是否进口\t否\n货号\tBK\n箱装数量\t120
```

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*