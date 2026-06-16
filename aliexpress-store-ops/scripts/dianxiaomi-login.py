#!/usr/bin/env python3
"""
店小秘 Auto-Login Script (Playwright)

Usage:
  python3 dianxiaomi-login.py [--user USERNAME] [--pass PASSWORD]

⚠️ 店小秘不支持邮箱登录！--user 参数必须填纯用户名（如 [你的店小秘用户名]），
   不能填邮箱（如 [你的店小秘邮箱]）。登录页源码会检测 @ 字符并拒绝。\n\nThis script opens a headless Chromium browser to 店小秘 login page,
fills credentials, shows the captcha, waits for the user to provide
the captcha code via file, then logs in and keeps the browser alive
for subsequent product editing.

File-based IPC:
  - Write captcha code to /tmp/dxm_code.txt
  - Write "STOP" to /tmp/dxm_code.txt to close the browser
  - Navigate: write "NAV:https://..." to /tmp/dxm_code.txt
  - Check state via /tmp/dxm_state.json
"""

import sys
import time
import json
import os
import urllib.request
import shutil
import argparse

from playwright.sync_api import sync_playwright

CODE_FILE = "/tmp/dxm_code.txt"
STATE_FILE = "/tmp/dxm_state.json"

def save_captcha(page):
    """Download captcha image to desktop and /tmp."""
    captcha_img = page.query_selector('img[src*="verify/code"]')
    if not captcha_img:
        print("NO_CAPTCHA_IMG")
        return False

    src = captcha_img.get_attribute("src")
    full_url = f"https:{src}" if src.startswith("//") else src
    urllib.request.urlretrieve(full_url, "/tmp/captcha_login.jpg")
    shutil.copy("/tmp/captcha_login.jpg", "C:/Users/[你的用户名]/Desktop/captcha_login.jpg")
    print(f"CAPTCHA_SAVED:{full_url}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="[你的店小秘用户名]",
                        help="店小秘用户名（不是邮箱！店小秘登录页会检测 @ 字符并拒绝邮箱登录）")
    parser.add_argument("--pass", dest="password", default="[你的店小秘密码]")
    args = parser.parse_args()

    for f in [CODE_FILE, STATE_FILE]:
        if os.path.exists(f):
            os.remove(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("https://www.dianxiaomi.com/index.htm", wait_until="domcontentloaded")
        time.sleep(2)

        page.fill("#exampleInputName", args.user)
        page.fill("#exampleInputPassword", args.password)
        print("CREDENTIALS_OK")

        if not save_captcha(page):
            print("FAILED: cannot get captcha")
            browser.close()
            sys.exit(1)

        with open(STATE_FILE, "w") as f:
            json.dump({"status": "waiting_for_code", "ts": time.time()}, f)
        print("WAITING_FOR_CAPTCHA_CODE")
        sys.stdout.flush()

        code = None
        for _ in range(600):
            if os.path.exists(CODE_FILE):
                with open(CODE_FILE) as f:
                    code = f.read().strip()
                if code:
                    break
            time.sleep(1)

        if not code:
            print("TIMEOUT")
            with open(STATE_FILE, "w") as f:
                json.dump({"status": "timeout"}, f)
            browser.close()
            sys.exit(1)

        print(f"FILLING_CAPTCHA:{code}")
        page.fill("#verifyCode", code)
        time.sleep(0.3)
        page.click("#loginBtn")
        print("LOGIN_CLICKED")
        time.sleep(3)

        time.sleep(3)
        current_url = page.url

        # Check login success by page content, not URL.
        # index.htm is used for BOTH the login page AND post-login homepage,
        # so URL alone cannot distinguish them.
        login_error = page.evaluate("""() => {
            const els = document.querySelectorAll('*');
            for (const el of els) {
                const t = el.textContent?.trim() || '';
                if (t.includes('验证码错误') || t.includes('密码错误') ||
                    t.includes('用户名不存在') || t.includes('账号不存在')) {
                    return t.slice(0, 100);
                }
            }
            return '';
        }""")

        if login_error:
            print(f"LOGIN_FAILED:{login_error}")
            with open(STATE_FILE, "w") as f:
                json.dump({"status": "failed", "error": login_error, "url": current_url}, f)
        else:
            print(f"LOGGED_IN:{current_url}")
            with open(STATE_FILE, "w") as f:
                json.dump({"status": "logged_in", "url": current_url}, f)

            if os.path.exists(CODE_FILE):
                os.remove(CODE_FILE)
            while True:
                time.sleep(2)
                if os.path.exists(CODE_FILE):
                    with open(CODE_FILE) as f:
                        cmd = f.read().strip()
                    os.remove(CODE_FILE)
                    if cmd == "STOP":
                        break
                    elif cmd.startswith("NAV:"):
                        url = cmd[4:]
                        page.goto(url, wait_until="domcontentloaded")
                        time.sleep(3)
                        print(f"NAVIGATED:{page.url}")
                        with open(STATE_FILE, "w") as f:
                            json.dump({"status": "navigated", "url": page.url}, f)
                        sys.stdout.flush()

        browser.close()
        print("DONE")


if __name__ == "__main__":
    main()
