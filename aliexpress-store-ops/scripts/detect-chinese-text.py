#!/usr/bin/env python3
"""
Detect Chinese text in images downloaded for 店小秘 image translation.

Usage:
    python3 scripts/detect-chinese-text.py <image_dir>

Where <image_dir> contains img_0.jpg, img_1.jpg, ... img_N.jpg

Output:
    For each image: [index] ✅ 有中文: <OCR text> or ❌ 无中文
    Summary at end: "有中文的图片: X 张"
"""

import os
import sys
import pytesseract
from PIL import Image

def has_chinese(text: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf' for c in text)

def main():
    img_dir = sys.argv[1] if len(sys.argv) > 1 else '/tmp/translate_imgs'
    
    if not os.path.isdir(img_dir):
        print(f"Directory not found: {img_dir}")
        sys.exit(1)
    
    results = []
    for i in range(100):  # max 100 images
        fpath = os.path.join(img_dir, f"img_{i}.jpg")
        if not os.path.exists(fpath):
            break
        
        try:
            img = Image.open(fpath)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng', config='--psm 6')
            text = text.strip()
            
            if has_chinese(text):
                chinese_chars = ''.join(c for c in text if '\u4e00' <= c <= '\u9fff')
                results.append((i, True, chinese_chars, text[:120]))
                print(f"[{i}] ✅ 有中文 [{chinese_chars}] | {text[:120]}")
            else:
                results.append((i, False, '', text[:60] or '(空)'))
                print(f"[{i}] ❌ 无中文 | OCR: {text[:60] if text else '(空)'}")
        except Exception as e:
            print(f"[{i}] ERROR: {e}")
    
    chinese_count = sum(1 for r in results if r[1])
    print(f"\n--- Summary ---")
    print(f"有中文的图片: {chinese_count} 张 / {len(results)} 张")
    for r in results:
        if r[1]:
            print(f"  [{r[0]}] {r[2]}")
    
    print(f"\n建议选择的索引: {[r[0] for r in results if r[1]]}")

if __name__ == '__main__':
    main()
