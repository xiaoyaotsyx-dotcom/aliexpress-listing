# 店小秘扫码登录（微信 QR 码）

## 触发条件

当以下所有条件满足时使用此方案：
- CDP 中继可用（Playwright connect_over_cdp 能连上）
- 但 OCR 验证码失败（ddddocr/tesseract 全部不通）
- 用户微信绑定了店小秘账号

## 步骤

### 1. 切换到扫码登录

```javascript
// 点击切换按钮
document.querySelector('.way-scan, .toggle-way').click();
```

触发的 handler: `DXM_LOGIN.switchToScanMethod(this)`

### 2. 刷新二维码

扫码区会显示「二维码已失效 点击刷新」。点击刷新链接：
```javascript
document.querySelector('.scan-img a, .shuffle-wechat a').click();
```

或者直接点击 `.scan-img` 区域：
```javascript
document.querySelector('.scan-img').click();
```

### 3. 获取二维码图片

```
https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={ticket_id}
```

用 Playwright evaluate 提取：
```javascript
var imgs = document.querySelectorAll('img');
for (var img of imgs) {
    if (img.src.includes('showqrcode') || img.src.includes('mp.weixin')) {
        return img.src;
    }
}
```

### 4. 发送给用户

下载二维码图片 → 通过 Feishu MEDIA 发送：
```python
import requests
resp = requests.get(qr_url, timeout=10)
with open('/tmp/dxm_qr.png', 'wb') as f:
    f.write(resp.content)
# 在回复中嵌入图片
# MEDIA:/tmp/dxm_qr.png
```

### 5. 等待扫码

用户用微信扫码后，店小秘自动登录。Playwright CDP 会话中的页面会跳转到主界面。

## ⚠️ 限制

- 需要用户手机配合扫码（不可自动化）
- QR code ticket 有时间限制，过期需刷新
- 仅首次登录有效——登录后 cookie 保存到 chrome-debug 配置中，下次启动无需重复扫码
- 用户可能未绑定微信到店小秘账号（未验证）

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*