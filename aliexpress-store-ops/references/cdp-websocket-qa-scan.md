# CDP WebSocket 全页 QA 扫描技术

## 问题
`browser_snapshot` 输出在 ~1500 行被截断，无法覆盖编辑页下半部分（SKU表、描述、包装、模板等）。

## 解决方案
用 `execute_code` Python 脚本通过 websocket 直连 CDP relay，执行 `Runtime.evaluate` 进行全页扫描。

## 连接方式
```python
import asyncio, json
import websockets

async def qa_scan():
    ws = await websockets.connect(
        "ws://127.0.0.1:19223/devtools/page/{targetId}",
        max_size=None
    )
    # 发送 Runtime.evaluate 命令
    msg = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "(() => { /* your JS */ })()",
            "returnByValue": True
        }
    }
    await ws.send(json.dumps(msg))
    resp = await asyncio.wait_for(ws.recv(), timeout=10)
    data = json.loads(resp)
    result = json.loads(data["result"]["result"]["value"])
    # process result
    await ws.close()

asyncio.run(qa_scan())
```

## 获取 targetId
```python
import subprocess, json
result = subprocess.run(["curl", "-s", "http://127.0.0.1:19223/json"], capture_output=True, text=True)
targets = json.loads(result.stdout)
dxm = [t for t in targets if 'dianxiaomi.com/web/smt/edit' in t['url']]
target_id = dxm[0]['id']
```

## 推荐扫描脚本

### 扫描所有表单字段（星号+值）
```javascript
(() => {
    const results = [];
    document.querySelectorAll('.ant-form-item').forEach(item => {
        const label = item.querySelector('.ant-form-item-label label');
        if (!label) return;
        const control = item.querySelector('.ant-form-item-control');
        const selItem = control?.querySelector('.ant-select-selection-item');
        const inp = control?.querySelector('input:not([type="hidden"]), textarea');
        let value = selItem ? selItem.textContent.trim() : (inp ? (inp.value || inp.placeholder) : '?');
        results.push({
            label: label.textContent.replace(/[\\*\\s:：]/g, '').trim().substring(0, 60),
            value: value.substring(0, 60),
            required: !!label.querySelector('.ant-form-item-required')
        });
    });
    return JSON.stringify(results);
})()
```

### 扫描页面指标
```javascript
(() => {
    const body = document.body.innerText;
    return JSON.stringify({
        chineseTitleError: body.includes('中文字符'),
        pleaseSelectCount: (body.match(/请选择/g) || []).length,
        hasWarnTriangle: body.includes('分类和速卖通推荐分类有较大差距'),
        totalBodyLength: body.length
    });
})()
```

### 精准定位空字段
```javascript
(() => {
    const results = [];
    document.querySelectorAll('.ant-select-selection-placeholder').forEach(ph => {
        const txt = ph.textContent.trim();
        if (txt === '请选择') {
            const formItem = ph.closest('.ant-form-item');
            let label = '';
            if (formItem) {
                const labelEl = formItem.querySelector('.ant-form-item-label label');
                label = labelEl ? labelEl.textContent.replace(/[\\*\\s:：]/g,'').trim().substring(0,50) : '';
            }
            const selectEl = ph.closest('[class*="ant-select"]');
            if (selectEl) {
                const rect = selectEl.getBoundingClientRect();
                results.push({ label, x: rect.left + rect.width/2, y: rect.top + rect.height/2 });
            }
        }
    });
    return JSON.stringify(results);
})()
```

## 优势
- 不受 browser_snapshot 截断限制
- 可一次性获取全部数据
- 返回结构化 JSON 便于程序化分析
- 比 browser_snapshot 更快（单次 CDP 往返）

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*