#!/usr/bin/env python3
"""
CDP 直连店小秘编辑脚本 — 无需验证码，复用用户 Chrome 登录态。

用法: 
  python3 scripts/dianxiaomi-cdp-edit.py [product_id]

前置条件:
  - Windows Chrome 调试模式运行中 (--remote-debugging-port=9222)
  - CDP 中继 (relay2.py) 运行中

工作流程:
  1. 通过 CDP 中继连接用户 Chrome
  2. 查找已打开的编辑页 tab，或新建 tab 打开编辑页
  3. 执行批量操作后退出
"""
import sys, time, json, os, urllib.request, re

# 配置
GW_CMD = "ip route show default | awk '{print $3}'"
CDP_PORT = 19223
DEFAULT_PRODUCT_ID = os.environ.get('PRODUCT_ID', '')

def get_gateway():
    """获取 WSL 网关 IP（CDP 中继地址）"""
    import subprocess
    gw = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True)
    gw_ip = gw.stdout.strip().split()[2] if gw.stdout.strip() else "172.24.48.1"
    return gw_ip

def connect_cdp(gw):
    """通过 CDP 中继连接用户 Chrome"""
    try:
        req = urllib.request.urlopen(f"http://{gw}:{CDP_PORT}/json/version", timeout=3)
        info = json.loads(req.read())
        ws_url = info["webSocketDebuggerUrl"]
        print(f"✅ CDP connected: Chrome/{info.get('Browser','?')}", flush=True)
        return ws_url
    except Exception as e:
        print(f"❌ CDP connection failed: {e}", flush=True)
        print(f"   确保 Chrome 调试模式和 relay2.py 已启动", flush=True)
        sys.exit(1)

def find_tab(browser, product_id):
    """在用户 Chrome 中查找已打开的编辑页"""
    from playwright.sync_api import sync_playwright
    for ctx in browser.contexts:
        for pg in ctx.pages:
            if product_id in pg.url and "edit" in pg.url:
                return pg
    return None

def main():
    product_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PRODUCT_ID
    if not product_id:
        print("用法: python3 dianxiaomi-cdp-edit.py <product_id>")
        print("或设置环境变量 PRODUCT_ID")
        sys.exit(1)

    gw = get_gateway()
    ws_url = connect_cdp(gw)
    
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        page = find_tab(browser, product_id)
        
        if not page:
            print(f"⚠️ Edit page not found in existing tabs. Opening new tab...", flush=True)
            page = browser.contexts[0].new_page()
            page.goto(f"https://www.dianxiaomi.com/web/smt/edit?id={product_id}", wait_until="networkidle")
        
        page.bring_to_front()
        time.sleep(4)  # Wait for React render
        
        # 获取页面基本状态
        info = page.evaluate('() => document.title')
        print(f"📄 Page: {info}", flush=True)
    
    # 示例：获取阻塞错误列表
    blockers = check_save_blockers(page)
    print(f"📋 保存阻塞数: {len(blockers)}")
    for b in blockers:
        print(f"   🔴 {b}")
    print()

    print("✅ CDP 连接就绪。此处可调用 fill_required_attributes() 等函数。", flush=True)


# ============================================================
# Helper: Ant Design Select 操作（CDP 模式已验证 2026-06-09）
# page.mouse.click() 必须用 real mouse event — JS .click() 不触发 dropdown
# ============================================================

def open_ant_select(page, label_contains):
    """
    按 form 标签名打开 Ant Design Select 下拉。
    返回 True/False。
    """
    pos = page.evaluate('(t) => {\n'
        'const items = document.querySelectorAll(".ant-form-item");\n'
        'for (const item of items) {\n'
        '  const label = item.querySelector(".ant-form-item-label label");\n'
        '  if (label && label.textContent.includes(t)) {\n'
        '    const sel = item.querySelector(".ant-select-selector");\n'
        '    if (sel) {\n'
        '      sel.scrollIntoView({block: "center"});\n'
        '      const r = sel.getBoundingClientRect();\n'
        '      return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};\n'
        '    }\n'
        '  }\n'
        '}\n'
        'return null;\n'
        '}', label_contains)
    if not pos:
        return False
    time.sleep(0.5)
    page.mouse.click(pos['x'], pos['y'])
    time.sleep(2)
    return True


def select_option(page, value_contains=''):
    """选下拉中第一个可见且含指定文字的选项。"""
    result = page.evaluate('(v) => {\n'
        'const opts = document.querySelectorAll(".ant-select-item-option");\n'
        'for (const opt of opts) {\n'
        '  if (opt.offsetParent !== null) {\n'
        '    const t = opt.textContent.trim();\n'
        '    if (!v || t.includes(v)) { opt.click(); return "OK: " + t; }\n'
        '  }\n'
        '}\n'
        'return "no match";\n'
        '}', value_contains)
    return result or 'no match'


def set_field_value(page, placeholder_contains, value):
    """用 nativeInputValueSetter 设置 React 受控组件的值。"""
    page.evaluate('(ph, val) => {\n'
        'const inp = document.querySelector(\'input[placeholder*="\' + ph + \'"]\');\n'
        'if (inp) {\n'
        '  const nt = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;\n'
        '  nt.call(inp, val);\n'
        '  inp.dispatchEvent(new Event("input", {bubbles: true}));\n'
        '  inp.dispatchEvent(new Event("change", {bubbles: true}));\n'
        '  inp.dispatchEvent(new Event("blur"));\n'
        '}\n'
        '}', placeholder_contains, value)


def navigate_to_tab(page, tab_name):
    """通过点击 tab 文字导航。如 '属性信息', '模版信息'"""
    page.evaluate('(tb) => {\n'
        'const all = document.querySelectorAll("*");\n'
        'for (const el of all) {\n'
        '  if (el.textContent && el.textContent.trim() === tb && el.offsetParent !== null) {\n'
        '    el.click(); return;\n'
        '  }\n'
        '}\n'
        '}', tab_name)
    time.sleep(2)


def extract_1688_params(page1688):
    """从 1688 详情页提取产品规格参数表。返回 dict。"""
    params = page1688.evaluate("""
        () => {
            const text = document.body.innerText || '';
            const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
            const result = {};
            const keywords = ['品牌','电压','功率','产地','风量','噪音','电源','认证',
                              '功能','材质','重量','颜色','保修','适用面积','净化方式',
                              '负离子','过滤','HEPA','型号','电池','充电','USB','档位','转速'];
            for (const kw of keywords) {
                for (const line of lines) {
                    if (line.includes(kw) && line.length < 100) {
                        if (!result[kw]) result[kw] = line;
                        break;
                    }
                }
            }
            const rows = document.querySelectorAll('tr');
            const tableRows = [];
            rows.forEach(tr => {
                const cells = tr.querySelectorAll('td, th');
                if (cells.length >= 2) {
                    const k = cells[0].textContent.trim();
                    const v = cells[1].textContent.trim();
                    if (k && v && k.length < 40 && v.length < 60)
                        tableRows.push(k + ': ' + v);
                }
            });
            return {keywords: result, tableRows: tableRows.slice(0, 40)};
        }
    """)
    return params


def fill_required_attributes(page, params_1688=None):
    """填写店小秘属性信息 tab 中的必填属性。"""
    navigate_to_tab(page, '属性信息')

    attr_map = [
        ('品牌',      '品牌',   'NONE'),
        ('产地',      '产地',   '中国大陆'),
        ('电压',      '电压',   '5'),
        ('功率',      '功率',   ''),
        ('风量',      '风量',   ''),
        ('HEPA',      'HEPA',   ''),
        ('高关注化学品', None,    ''),
    ]

    for label, kw, default_val in attr_map:
        val_to_find = default_val
        if params_1688 and kw:
            for p in params_1688.get('tableRows', []):
                if kw in p and ':' in p:
                    val_to_find = p.split(':', 1)[1].strip()
                    break

        if open_ant_select(page, label):
            result = select_option(page, val_to_find or '')
            print(f"  {label}: {result}", flush=True)
            time.sleep(1)
        else:
            print(f"  {label}: not found", flush=True)


def check_save_blockers(page):
    """保存前检查哪些错误会阻塞保存，返回错误列表。"""
    return page.evaluate("""
        () => {
            const errs = document.querySelectorAll('.ant-form-item-explain-error');
            return Array.from(errs).filter(e => e.offsetParent !== null).map(e => {
                const item = e.closest('.ant-form-item');
                const label = item ? item.querySelector('.ant-form-item-label label') : null;
                return (label ? label.textContent.trim() : '?') + ': ' + e.textContent.trim().substring(0, 60);
            });
        }
    """)


if __name__ == "__main__":
    main()
