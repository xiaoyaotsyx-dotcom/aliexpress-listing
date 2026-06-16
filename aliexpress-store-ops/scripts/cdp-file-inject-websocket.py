"""
CDP WebSocket 文件注入脚本
通过 WebSocket 直接向浏览器页面注入文件（base64 -> File() 构造函数）
适用于 CDP setInputFiles 不可用的场景
"""
import json, asyncio, base64
import websockets

CDP_WS = 'ws://127.0.0.1:19223/devtools/browser/<BROWSER_ID>'
TARGET_ID = '<PAGE_TARGET_ID>'
PDF_PATH = '/mnt/c/Users/[你的Windows用户名]/Desktop/风扇说明书.pdf'

async def main():
    async with websockets.connect(CDP_WS, max_size=10*1024*1024, ping_interval=None) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Target.attachToTarget", "params": {"targetId": TARGET_ID, "flatten": True}}))
        session_id = None
        while not session_id:
            resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
            if resp.get('method') == 'Target.attachedToTarget':
                session_id = resp['params']['sessionId']
        with open(PDF_PATH, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        js = f'''(async function() {{
            try {{
                var b64 = "{b64}";
                var binaryStr = atob(b64);
                var bytes = new Uint8Array(binaryStr.length);
                for (var i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);
                var file = new File([bytes], '{PDF_PATH.split("/")[-1]}', {{type: 'application/pdf'}});
                var input = document.querySelector('#localFileUploadInp');
                if (!input) return JSON.stringify({{ok: false, error: 'no input'}});
                var dt = new DataTransfer();
                dt.items.add(file);
                input.files = dt.files;
                ['change', 'input', 'blur'].forEach(function(n) {{ input.dispatchEvent(new Event(n, {{bubbles: true}})); }});
                return JSON.stringify({{ok: true, size: file.size, files: input.files.length}});
            }} catch(e) {{ return JSON.stringify({{ok: false, error: e.message}}); }}
        }})()'''
        await ws.send(json.dumps({"id": 2, "sessionId": session_id, "method": "Runtime.evaluate", "params": {"expression": js, "returnByValue": True, "awaitPromise": True, "timeout": 120000}}))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=120))
        print(resp.get('result', {}).get('result', {}).get('value', 'FAIL'))

asyncio.run(main())
