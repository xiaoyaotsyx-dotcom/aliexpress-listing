# Vue 3 组件内部状态检查（店小秘调试用）

店小秘使用 Vue 3 + Ant Design Vue。CDP 模式下，有时需要通过 Vue 内部状态定位问题。

## 查找 Vue App 实例

```javascript
// Vue 3 将 __vue_app__ 附加在 #app 容器上
var app = document.getElementById('app').__vue_app__;
// app 的可用字段：
//   _component — 根组件
//   _container — DOM 容器
//   version    — Vue 版本字符串
//   config     — 全局配置
// app._instance — 根组件实例（生产构建中可能为 null）
```

⚠️ 店小秘是 production build，`_instance` 可能为 null。不要依赖 Vue 内部接口做自动化。

## 识别组件作用域

每个 Vue 组件有唯一 `data-v-xxxxxx` 属性，可通过它反向找组件：

```javascript
// 找特定 scoped 属性的组件
document.querySelector('[data-v-3f369f9f]')
// 该属性的值对应组件编译时的 scope ID
```

## 检查 DOM 节点上的 Vue 属性

```javascript
Object.keys(element).filter(k => k.startsWith('__vue') || k.startsWith('__v'))
// 店小秘 production build 中 DOM 元素上通常无可用 Vue 内部属性
```

## 用 CDP DOM.getDocument 定位深层节点

当 CSS 选择器找不到元素时，用 CDP `DOM.getDocument({depth: -1})` 获取完整 DOM 树。

```bash
# 1. 获取完整 DOM 树（~6MB JSON，保存到文件）
# 通过 browser_cdp: {method: "DOM.getDocument", params: {depth: -1}, target_id: "..."}

# 2. 搜索目标属性
grep -oP '.{0,100}目标属性.{0,100}' /tmp/dom_tree.json

# 3. 从匹配行提取 backendNodeId
# "backendNodeId": 15402

# 4. 用 backendNodeId 调用 CDP 方法
# DOM.setFileInputFiles, DOM.describeNode 等
```

⚠️ `nodeId` 会随 DOM 变化而失效。`backendNodeId` 在元素生命周期内稳定。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*