# Chrome Cookie 数据库与 CDP 登录

## 背景

当需要自动化访问已登录的店小秘时，一个自然的想法是复制 Chrome 的 Cookie 数据库。**此路不通。**

## 为什么 cookie 拷贝不可行

Chrome 148+ 中，cookie 值使用 **AES 加密** 存储。加密密钥存储在 profile 的 `Local State` 文件中。不同 profile 有不同的密钥。即使复制了整个 `Local State` + `Cookies` 数据库，Chrome 可能因为路径签名或其他完整性检查失败而拒绝使用。

### 验证记录

| 尝试 | 结果 | 说明 |
|:--|:--:|:--|
| 读取 chrome-debug cookie DB 中 店小秘 cookie 值 | 值为空字符串 | Chrome 加密存储，SQLite 直接读内容为空 |
| 拷贝 Default profile 的 `Cookies` 到 chrome-debug | 导航后仍在登录页 | cookie 无法被 chrome-debug 的密钥解密 |
| 同时拷贝 `Local State` + `Cookies` | 同样失败 | 路径签名或加密机制不同 |
| 用 `Network.setCookie` CDP 注入 | 未验证 | 需要知道明文 cookie 值（无法获取） |

## 可靠路径

复用用户 Chrome 的已有登录态（通过 CDP），不依赖 cookie 拷贝或自动化登录。

---

*作者: Rigi AI Commons | 小红书 @瑞吉AI人民公社 | AI自动化专家工作流*