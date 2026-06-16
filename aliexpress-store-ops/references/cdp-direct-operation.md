# CDP 直连操作模式（当 browser_navigate/snapshot 不可用时）

## 触发条件

当 browser_navigate、browser_snapshot、browser_console 等 Hermes 浏览器工具报以下错误时，它们不可用但 browser_cdp 仍然可用：

```
Auto-launch failed: CDP WebSocket connect failed: HTTP error: 404 Not Found
```

设置 `browser.engine: cdp` 无法解决此问题——auto-launch 机制仍会介入。

## 解决方案：使用 browser_cdp 代替所有浏览器操作

browser_cdp 通过 CDP 直连工作，绕过 auto-launch，在 TCP 中继环境下正常工作。

### 获取可用标签页

```
browser_cdp(method='Target.getTargets', params={})
```

返回当前浏览器所有 target（页面、iframe），每个含 targetId、title、url。

### 导航现有标签页

```
browser_cdp(method='Page.navigate', params={"url":"https://..."}, target_id=<targetId>)
```

### 在页面中执行 JavaScript

```
browser_cdp(method='Runtime.evaluate', params={"expression":"...JS...","returnByValue":true}, target_id=<targetId>)
```

### 创建新标签页

```
browser_cdp(method='Target.createTarget', params={"url":"https://..."})
```

返回新 targetId，页面自动加载 URL。

### 截图

```
browser_cdp(method='Page.captureScreenshot', params={"format":"png"}, target_id=<targetId>)
```

返回 base64 data，需保存到文件后用 MEDIA: 分享。

### 发送鼠标事件（点击）

```
# mousePressed
browser_cdp(method='Input.dispatchMouseEvent', params={"button":"left","clickCount":1,"type":"mousePressed","x":X,"y":Y}, target_id=<targetId>)
# mouseReleased
browser_cdp(method='Input.dispatchMouseEvent', params={"button":"left","clickCount":1,"type":"mouseReleased","x":X,"y":Y}, target_id=<targetId>)
```

⚠️ 对于 Vue 3 事件绑定，真实鼠标事件比 JS `.click()` 更可靠。

## 弹窗拦截器绕过（href="javascript:" 编辑链接）

店小秘采集箱的「编辑」链接使用 `href="javascript:"` + Vue 事件处理器，内部调用 `window.open()` 在新标签页打开编辑页。JavaScript `.click()` 触发弹窗会被浏览器拦截。

### 解决方案：钩子 + Target.createTarget

```javascript
// 1. 钩子 window.open 捕获 URL
window._capturedUrl=null;
window._origOpen=window.open;
window.open=function(url,...args){
  window._capturedUrl=url;
  return window._origOpen.call(window,url,...args);
};

// 2. JS 点击编辑链接
document.querySelector('a编辑').click();

// 3. 读取捕获的 URL
// → "/web/smt/edit?id=[PHONE_REDACTED]5180676"

// 4. 用 CDP 创建新标签页
browser_cdp(method='Target.createTarget', params={"url":"https://www.dianxiaomi.com/web/smt/edit?id=[PHONE_REDACTED]5180676"})

// 5. 恢复 window.open
window.open=window._origOpen;
delete window._origOpen;
delete window._capturedUrl;
```

### 从行 HTML 找产品 ID 的替代方法

如果不能钩子 window.open，可以搜索行 HTML 中的产品 ID：

```javascript
// 行 HTML 中包含产品 ID 的关键模式
const rowHTML = row.innerHTML;
// 搜索: /smt\/edit[^"']*id=(\d+)/ 或 Vue data 属性
```

## 注意事项

- 每次操作必须指定正确的 `target_id`（从 Target.getTargets 获取）
- 编辑页 target_id 在整个操作过程中保持不变，不要混用采集箱页的 target_id
- 截图结果太大时需要保存到文件，用 MEDIA: 分享
- `window.open` 钩子在页面刷新后失效，每次需要重新设置

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*