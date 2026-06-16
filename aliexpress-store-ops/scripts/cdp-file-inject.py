#!/usr/bin/env python3
"""
CDP WebSocket 文件注入工具
===========================
通过 Chrome DevTools Protocol WebSocket 将本地文件注入到页面中的 <input type="file">。
绕过 Hermes browser_cdp 的表达式长度限制，适合大文件（如 PDF）。

用法：
  python3 cdp-file-inject.py <pdf_path> [target_id] [cdp_url]

参数：
  pdf_path   本地 PDF 文件路径（Windows 格式：C:\\path\\to\\file.pdf）
  target_id  可选，页面 Target ID（默认自动查找 smt/edit 页面）
  cdp_url    可选，CDP WebSocket URL（默认 ws://127.0.0.1:19223/...）

前置条件：
  - Chrome CDP 中继已启动
  - 店小秘编辑页已打开

限制：
  - 注入后 Vue 3 重渲染会清除文件，此脚本仅用于调试验证
  - 生产环境仍需用户手动操作
"""
import json, asyncio, base64, sys, os

# Default CDP WebSocket URL (will be discovered if not provided)
DEFAULT_CDP_HOST = 'http://127.0.0.1:19223'

def find_cdp_url():
    """Auto-discover CDP WebSocket URL from relay endpoint"""
    import urllib.request
    try:
        resp = urllib.request.urlopen(f'{DEFAULT_CDP_HOST}/json/version', timeout=5)
        data = json.loads(resp.read())
        return data['webSocketDebuggerUrl']
    except Exception as e:
        print(f"ERROR: Cannot discover CDP URL: {e}")
        print(f"Make sure the CDP relay is running and accessible at {DEFAULT_CDP_HOST}")
        sys.exit(1)

def find_page_target(cdp_http):
    """Find the smt/edit page target ID"""
    import urllib.request
    try:
        resp = urllib.request.urlopen(f'{cdp_http}/json', timeout=5)
        pages = json.loads(resp.read())
        for p in pages:
            if p['type'] == 'page' and 'smt/edit' in p['url']:
                return p['id']
        # Fallback: return first page
        for p in pages:
            if p['type'] == 'page':
                print(f"WARN: No smt/edit page found. Using: {p['title'][:50]}")
                return p['id']
        print("ERROR: No page targets found")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Cannot list pages: {e}")
        sys.exit(1)

async def inject_file(cdp_ws_url, target_id, file_path):
    """Inject a file into the page via CDP WebSocket"""
    import websockets
    
    # Read and encode file
    with open(file_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    
    file_name = os.path.basename(file_path)
    file_size = len(b64)  # approximately
    print(f"File: {file_name} ({file_size} chars base64)")
    
    js_code = f'''
(async function() {{
    try {{
        var b64 = "{b64}";
        var binaryStr = atob(b64);
        var bytes = new Uint8Array(binaryStr.length);
        for (var i = 0; i < binaryStr.length; i++)
            bytes[i] = binaryStr.charCodeAt(i);
        var file = new File([bytes], '{file_name}', {{type: 'application/pdf'}});
        var input = document.querySelector('#localFileUploadInp');
        if (!input) return JSON.stringify({{ok: false, error: 'input not found'}});
        var dt = new DataTransfer();
        dt.items.add(file);
        input.files = dt.files;
        ['change', 'input', 'blur'].forEach(function(n) {{
            input.dispatchEvent(new Event(n, {{bubbles: true}}));
        }});
        return JSON.stringify({{
            ok: true, size: file.size, files: input.files.length,
            name: input.files[0].name,
            hasError: !!document.querySelector('.ant-form-item-has-error')
        }});
    }} catch(e) {{
        return JSON.stringify({{ok: false, error: e.message}});
    }}
}})()
'''
    
    async with websockets.connect(cdp_ws_url, max_size=10*1024*1024, ping_interval=None) as ws:
        msg_id = [1]
        pending = {}
        
        async def recv_loop():
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                    mid = msg.get('id')
                    if mid in pending:
                        pending[mid].set_result(msg)
                except:
                    pass
        
        async def send(method, params, use_session=False, session_id=None):
            mid = msg_id[0]
            msg_id[0] += 1
            payload = {"id": mid, "method": method, "params": params}
            if use_session and session_id:
                payload["sessionId"] = session_id
            future = asyncio.Future()
            pending[mid] = future
            await ws.send(json.dumps(payload))
            result = await asyncio.wait_for(future, timeout=60)
            del pending[mid]
            return result
        
        # Start message loop
        loop_task = asyncio.create_task(recv_loop())
        await asyncio.sleep(0.3)
        
        # Attach to target
        resp = await send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = resp.get('result', {}).get('sessionId')
        if not session_id:
            print("ERROR: Failed to attach to target")
            return
        await asyncio.sleep(0.5)
        
        print(f"Attached to target {target_id[:20]}... session: {session_id[:20]}...")
        print(f"Sending evaluate ({len(js_code)} chars)...")
        
        result = await send("Runtime.evaluate", {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": True,
            "timeout": 120000
        }, use_session=True, session_id=session_id)
        
        val = result.get('result', {}).get('result', {}).get('value', 'N/A')
        print(f"Result: {val}")
        
        loop_task.cancel()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    file_path = sys.argv[1]
    target_id = sys.argv[2] if len(sys.argv) > 2 else None
    cdp_url = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    
    # Auto-discover CDP URL and target
    cdp_http = DEFAULT_CDP_HOST
    if not cdp_url:
        cdp_url = find_cdp_url()
    if not target_id:
        target_id = find_page_target(cdp_http)
    
    print(f"CDP: {cdp_url}")
    print(f"Target: {target_id}")
    
    asyncio.run(inject_file(cdp_url, target_id, file_path))

if __name__ == '__main__':
    main()
