#!/usr/bin/env python3
"""
保存前检查 — 检测哪些因素会阻塞「保存并移入待发布」。

用法:
  python3 scripts/dianxiaomi-check-blockers.py [product_id]

检测项:
  - 标题含中文
  - 必填属性缺失
  - 包装尺寸非整数
"""
import sys, time, json
from playwright.sync_api import sync_playwright

GW = "172.24.48.1"

def find_page(browser, product_id):
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if product_id in pg.url and "edit" in pg.url:
                return pg
    return None

def main():
    product_id = sys.argv[1] if len(sys.argv) > 1 else "[PHONE_REDACTED]5663520"
    import urllib.request
    gw = GW
    req = urllib.request.urlopen(f"http://{gw}:19223/json/version", timeout=5)
    ws_url = json.loads(req.read())["webSocketDebuggerUrl"]
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = find_page(browser, product_id)
        if not page:
            print("Edit page not found")
            sys.exit(1)
        
        page.bring_to_front()
        time.sleep(4)
        
        # Check title for Chinese
        title_check = page.evaluate("""() => {
            const inputs = document.querySelectorAll('input[type="text"]');
            for (const inp of inputs) {
                const v = inp.value || '';
                if (v.includes('净化器') || v.includes('空气') || v.length > 20) {
                    const hasChinese = [...v].some(c => c > '\\u4e00' && c < '\\u9fff');
                    return {title: v.substring(0, 60), hasChinese: hasChinese, length: v.length};
                }
            }
            return {title: 'not found', hasChinese: false, length: 0};
        }""")
        print(f"标题: {'含中文' if title_check.get('hasChinese') else 'OK'} len={title_check.get('length')}")
        
        # Check form errors
        errors = page.evaluate("""() => {
            const errs = document.querySelectorAll('.ant-form-item-explain-error');
            return Array.from(errs).filter(e => e.offsetParent !== null).map(e => {
                const item = e.closest('.ant-form-item');
                const label = item ? item.querySelector('.ant-form-item-label label') : null;
                return (label ? label.textContent.trim() : '?') + ': ' + e.textContent.trim().substring(0, 40);
            });
        }""")
        print(f"错误数: {len(errors)}")
        for e in errors:
            print(f"  {e}")

if __name__ == "__main__":
    main()
