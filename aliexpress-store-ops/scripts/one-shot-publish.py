#!/usr/bin/env python3
"""
one-shot-publish.py — 店小秘一键填表+发布脚本（路径 B）

策略：先移入待发布 → 再编辑 → 保存并移入待发布（一次性提交）
⚠️ 绝不混合使用 browser_navigate + Playwright 操作同一编辑页！
"""
from playwright.sync_api import sync_playwright
import time

PRODUCT_ID = "[PHONE_REDACTED]5663520"
NEW_TITLE = "Mini Neck Air Purifier Portable Necklace Personal Air Freshener Wearable Air Cleaner"

REQUIRED_ATTRS = [
    ('品牌(Brand Name)', 'NONE(NONE)'),
    ('电压(Voltage)', 'DC5V'),
    ('产地（国家或地区）(Origin)', '中国大陆'),
    ('风量(Air Volume)', '50'),
    ('功率(瓦)(Power (W))', '1'),
    ('HEPA滤网等级(HEPA Grade)', '其他'),
    ('高关注化学品(High-concerned chemical)', '天然'),
    ('噪音(Noise)', '35'),
]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:19223')
    ctx = browser.contexts[0]

    # Step 1: 移入待发布（从采集箱列表）
    target = ctx.new_page()
    target.goto('https://www.dianxiaomi.com/web/smt/smtProductList/draft')
    time.sleep(4)
    target.evaluate(f"""() => {{
        var inp = document.querySelector('input[placeholder*="搜索"]');
        if (inp) {{
            var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(inp, '{PRODUCT_ID}');
            inp.dispatchEvent(new Event('input', {{bubbles: true}})); }}}}""")
    time.sleep(0.5)
    target.evaluate("""() => {
        for (var b of document.querySelectorAll('button'))
            if (b.textContent.trim() === '搜索' && b.offsetParent) { b.click(); return; } }""")
    time.sleep(3)
    target.evaluate("""() => {
        for (var r of document.querySelectorAll('tr'))
            for (var b of r.querySelectorAll('button, a, span'))
                if (b.textContent.trim() === '移入待发布') { b.click(); return; } }""")
    time.sleep(2)
    target.evaluate("""() => {
        for (var b of document.querySelectorAll('button, .ant-btn-primary, .ant-btn'))
            if (b.textContent.includes('确') && b.textContent.includes('定') && b.offsetParent) { b.click(); return; } }""")
    time.sleep(3)

    # Step 2: 打开编辑页
    target = ctx.new_page()
    target.goto(f'https://www.dianxiaomi.com/web/smt/edit?id={PRODUCT_ID}')
    time.sleep(5)

    # Step 3: 标题
    target.evaluate(f"""() => {{
        var inp = document.querySelector('input[placeholder*="标题"]');
        if (inp) {{
            var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(inp, '{NEW_TITLE}');
            inp.dispatchEvent(new Event('input', {{bubbles: true}})); }}}}""")

    def fill_sel(label_kw, opt_search):
        cd = target.evaluate("""(kw) => {
            for (var i of document.querySelectorAll('.ant-form-item')) {
                var l = i.querySelector('.ant-form-item-label label');
                if (l && l.textContent.includes(kw)) {
                    var s = i.querySelector('.ant-select-selector');
                    if (s) { s.scrollIntoView({block:'center'});
                        var r = s.getBoundingClientRect();
                        return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)}; }}}
            return null; }""", label_kw)
        if not cd: return
        target.mouse.click(cd['x'], cd['y']); time.sleep(1.5)
        target.evaluate(f"""() => {{
            for (var o of document.querySelectorAll('.ant-select-item-option'))
                if (o.offsetParent && o.textContent.includes('{opt_search}')) {{ o.click(); return; }}}}""")
        time.sleep(0.3); target.mouse.click(200, 300); time.sleep(0.3)

    for l, s in REQUIRED_ATTRS: fill_sel(l, s)

    # Step 4: 上传说明书
    target.evaluate("document.querySelector('.manual-upload')?.scrollIntoView({block:'center'})")
    time.sleep(1)
    with target.expect_file_chooser(timeout=15000) as fc:
        target.evaluate("""() => {
            for (var b of document.querySelectorAll('button'))
                if (b.textContent.trim() === '上传文件' && b.offsetParent) { b.click(); return; } }""")
        time.sleep(2)
        target.evaluate("""() => {
            for (var item of document.querySelectorAll('.ant-dropdown-menu-item'))
                if (item.textContent.includes('本地上传') && !item.textContent.includes('空间'))
                    { item.click(); return; } }""")
        time.sleep(2.5)
        target.evaluate("document.querySelector('#localFileUploadInp')?.click()")
        time.sleep(2)
    fc.value.set_files('/mnt/c/Users/[你的Windows用户名]/Desktop/风扇说明书.pdf')
    time.sleep(3)

    def click_tab(name):
        target.evaluate("""(n) => { for (var l of document.querySelectorAll('a'))
            if (l.textContent.trim() === n && l.offsetParent) { l.click(); return; } }""", name)
        time.sleep(2)

    # Step 5: 包装
    click_tab('包装信息')
    target.evaluate("""() => {
        var inp = document.getElementById('form_item_grossWeight');
        if (inp) { var s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            s.call(inp, '0.045'); inp.dispatchEvent(new Event('input', {bubbles: true})); } }""")
    target.evaluate("""() => {
        var dims = ['6','3','2'];
        for (var l of document.querySelectorAll('label'))
            if (l.textContent.includes('包装后尺寸')) {
                var fi = l.closest('.ant-form-item');
                if (fi) { var idx = 0;
                    for (var inp of fi.querySelectorAll('input'))
                        if (inp.offsetParent && idx < dims.length) {
                            var s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
                            s.call(inp, dims[idx]); idx++; } } } }""")

    # Step 6: 模版
    click_tab('模版信息')
    fill_sel('运费模板', '5-8美金')
    fill_sel('服务模板', 'Service')
    fill_sel('欧盟责任人', 'MJCM')
    fill_sel('品牌制造商', 'Jiuye')

    # Step 7: 其他信息
    click_tab('其他信息')
    target.evaluate("""() => {
        for (var r of document.querySelectorAll('.ant-radio-wrapper'))
            if (r.textContent.includes('不含关税') && !r.classList.contains('ant-radio-wrapper-checked')) { r.click(); } }""")

    # Step 8: 保存并移入待发布
    target.evaluate("""() => {
        for (var b of document.querySelectorAll('button'))
            if (b.textContent.includes('保存并移入') && b.offsetParent) { b.click(); return; } }""")
    time.sleep(5)
    errs = target.evaluate("""() => Array.from(document.querySelectorAll('.ant-form-item-explain-error'))
        .filter(e => e.offsetParent).map(e => e.textContent.trim())""")
    if errs: print(f"Errors: {errs}")
    else: print("Success!")
    browser.close()
