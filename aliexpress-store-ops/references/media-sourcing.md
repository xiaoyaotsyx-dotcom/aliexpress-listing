# 店小秘 1688 媒体资源获取

> 从 1688 产品页获取图片和视频，上传到店小秘。

## 查找视频

### 方法1：HTML 源码搜索
1688 产品页的 HTML 中可能直接包含视频 URL：
```python
pageText = page.evaluate("() => document.documentElement.outerHTML")
import re
video_urls = re.findall(r'https?://[^"\']+\.(mp4|webm)[^"\']*', pageText)
# 常见格式：https://cloud.video.taobao.com/play/u/{user_id}/p/2/e/6/t/1/{video_id}.mp4
```

### 方法2：检查 video 元素
```python
videos = page.evaluate("""
    () => {
        const vids = document.querySelectorAll('video');
        return Array.from(vids).map(v => ({
            src: v.currentSrc || v.querySelector('source')?.src || ''
        }));
    }
""")
```

### 方法3：检查视频播放器容器
1688 页面可能有「主图视频」或「讲解视频」标识：
```python
# 检查文本
text = page.evaluate("() => document.body.innerText")
if '主图视频' in text or '讲解视频' in text:
    print("视频区域存在")
```

## 下载视频

```python
import urllib.request
video_url = "https://cloud.video.taobao.com/play/u/22[PHONE_REDACTED]/p/2/e/6/t/1/506132133269.mp4"
req = urllib.request.Request(video_url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = resp.read()
    with open('/mnt/d/video.mp4', 'wb') as f:
        f.write(data)
```

## 上传到店小秘

店小秘的产品视频上传使用隐藏的 `<input type="file" id="localFileUploadInp">`。

```python
# 方式1：直接 set_input_files（推荐）
file_input = page.locator('#localFileUploadInp').first
file_input.set_input_files("/mnt/d/video.mp4", timeout=15000)
time.sleep(3)

# 验证上传状态
status = page.evaluate("""
    () => {
        const text = document.body.innerText;
        if (text.includes('审核成功')) return '审核成功 ✅';
        if (text.includes('播放')) return '可播放 ✅';
        return text.includes('重新上传') ? '待上传' : '未知';
    }
""")
```

### 注意事项
- `set_input_files` 参数必须是 WSL 路径（`/mnt/d/...`），不是 Windows 路径
- 视频限 100MB 内
- 上传后阿里云会自动审核，状态显示「审核成功」或「播放」
- 不要上传带工厂 logo 的视频（用户要求"产品视频，不是工厂视频"）

## 获取产品图片

1688 图片 URL 格式（原始 JPEG）：
```
https://cbu01.alicdn.com/img/ibank/O1CN{hash}_!!{user_id}-0-cib.jpg
```

前端展示的是 webp 格式（加 `_.webp` 后缀），请求时去掉后缀获得高质量原图。

```python
image_urls = page.evaluate("""
    () => {
        const imgs = document.querySelectorAll('img');
        const urls = [];
        for (const img of imgs) {
            const src = img.src || '';
            if (src.includes('cbu01.alicdn.com') && !src.includes('logo')) {
                // 去掉 .webp 获得原始 JPG
                const rawJpg = src.replace(/\.(webp|jpg)_.*$/, '');
                if (rawJpg && !urls.includes(rawJpg)) urls.push(rawJpg);
            }
        }
        return urls.slice(0, 12);
    }
""")
```

## 判断视频类型

用户区分两类视频：
- ✅ **产品视频**：展示产品外观、功能、使用场景（需上传）
- ❌ **工厂视频**：展示生产线、工厂环境、车间（不用）

判断依据：页面中「主图视频」标签旁的描述文字、视频封面的内容。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*