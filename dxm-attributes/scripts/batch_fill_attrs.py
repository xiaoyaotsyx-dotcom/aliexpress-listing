#!/usr/bin/env python3
"""
批量填写店小秘产品属性 + 删除自定义属性
用法: python3 batch_fill_attrs.py <ws_url> <target_id>

策略：
1. 先检查每个字段当前值，已填对的跳过
2. 未填或用值不匹配的，打开下拉选值
3. 最后的自定义属性批量删除
"""
import websocket, json, time, sys

WS_URL = sys.argv[1] if len(sys.argv) > 1 else ''
TARGET_ID = sys.argv[2] if len(sys.argv) > 2 else ''
if not WS_URL or not TARGET_ID:
    print("Usage: python3 batch_fill_attrs.py <ws_url> <target_id>"); sys.exit(1)

ATTRIBUTES = [
    ("产地（国家或地区）", "中国大陆"),
    ("品牌(Brand Name)", "NONE"),
    ("高关注化学品", "天然未处理"),
    ("品种大小", "所有包装"),
    ("类型(Type)", "狗狗"),
    ("图案类型", "纯色"),
    ("风格(Style)", "fashion"),
    ("适应犬种", "通用"),
    ("材质(Material)", "硅胶"),
]

class CDP:
    def __init__(self, ws):
        self.ws = websocket.create_connection(ws, timeout=30, header={"Origin": "http://localhost:19223"})
        self.mid = 1000; self.sid = None

    def _cmd(self, m, p=None):
        self.mid += 1; msg = {"id": self.mid, "method": m}
        if p: msg["params"] = p
        if self.sid: msg["sessionId"] = self.sid
        self.ws.send(json.dumps(msg))

    def _recv(self):
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self.mid: return r

    def call(self, m, p=None): self._cmd(m, p); return self._recv()

    def js(self, expr):
        r = self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        return r.get("result", {}).get("result", {}).get("value")

    def mouse(self, t, x, y):
        self.call("Input.dispatchMouseEvent", {"type": t, "x": x, "y": y, "button": "left", "clickCount": 1})

    def attach(self):
        self.sid = self.call("Target.attachToTarget", {"targetId": TARGET_ID, "flatten": True})["result"]["sessionId"]
        print(f"✓ Attached: {self.sid[:20]}...")

    def switch_tab(self, name):
        if self.js(f"""
            (() => {{ const items = document.querySelectorAll('.anchor-menu-item');
                for (const i of items) if (i.textContent.trim() === '{name}') {{ i.click(); return 1; }}
                return 0; }})()
        """):
            print(f"  → {name}"); time.sleep(1); return True
        return False

    def hide_drops(self):
        self.js("document.querySelectorAll('.ant-select-dropdown').forEach(d => d.style.display='none');")

    def get_select_state(self, label_kw):
        """返回 (found, current_value, coords)"""
        return self.js(f"""
            (() => {{
                const items = document.querySelectorAll('.ant-form-item');
                for (const item of items) {{
                    const label = item.querySelector('.ant-form-item-label label');
                    if (label && label.textContent.includes('{label_kw}')) {{
                        const sel = item.querySelector('.ant-select-selector');
                        if (!sel) return JSON.stringify([0, '', null]);
                        // 读当前值
                        const cur = sel.querySelector('.ant-select-selection-item');
                        const val = cur ? cur.textContent.trim() : '';
                        // 滚动
                        const scrollArea = document.querySelector('.main-content, [class*=\"scroll\"], .ant-layout-content');
                        if (scrollArea) scrollArea.scrollTop = scrollArea.scrollTop + sel.getBoundingClientRect().top - 300;
                        // 坐标
                        const r = sel.getBoundingClientRect();
                        return JSON.stringify([1, val, {{x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)}}]);
                    }}
                }}
                return JSON.stringify([0, '', null]);
            }})()
        """)

    def close(self): self.ws.close()


def main():
    print(f"Target: {TARGET_ID[:20]}...")
    c = CDP(WS_URL); c.attach()

    if not c.switch_tab("属性信息"):
        print("✗ 无法切换 tab"); c.close(); return

    ok = skip = fail = 0
    for label, want in ATTRIBUTES:
        state = json.loads(c.get_select_state(label))
        found, current, coords = state[0], state[1], state[2]

        if not found:
            print(f"  ⚠ {label}: not found"); fail += 1; continue

        # Check if already set
        if current and (want in current or current.startswith(want.split('(')[0])):
            print(f"  ✓ {label}: already '{current}'"); skip += 1; continue

        # Need to fill
        c.hide_drops(); time.sleep(0.05)

        # Open dropdown
        c.mouse("mousePressed", coords["x"], coords["y"])
        c.mouse("mouseReleased", coords["x"], coords["y"])
        time.sleep(0.3)

        # Try to select
        result = c.js(f"""
            (() => {{
                const drops = document.querySelectorAll('.ant-select-dropdown');
                for (const d of drops) {{
                    if (d.style.display === 'none') continue;
                    const items = d.querySelectorAll('.ant-select-item-option');
                    if (!items.length) continue;
                    for (const item of items) {{
                        const t = item.textContent.trim();
                        if (t.startsWith('{want}') || t === '{want}' || t.includes('{want}')) {{
                            item.click(); return 'OK';
                        }}
                    }}
                }}
                return 'NF';
            }})()
        """)

        if result == 'OK':
            print(f"  ✅ {label} → {want}"); ok += 1
        else:
            # Show available options
            opts = c.js("""
                (() => {
                    const drops = document.querySelectorAll('.ant-select-dropdown');
                    const all = [];
                    drops.forEach(d => {
                        if (d.style.display === 'none') return;
                        d.querySelectorAll('.ant-select-item-option').forEach(o => all.push(o.textContent.trim().substring(0,50)));
                    });
                    return JSON.stringify(all.slice(0,15) || ['NO_OPTIONS']);
                })()
            """)
            print(f"  ❌ {label}: '{want}' not found. Options: {opts}"); fail += 1

    print(f"\n{'='*40}")
    print(f"✅ {ok} new  ✓ {skip} already-set  ❌ {fail} fail")
    c.close()

if __name__ == "__main__":
    main()
