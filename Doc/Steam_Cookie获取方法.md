# Steam Cookie 获取方法

## 🚀 方法一：使用 getAppToken 工具（自动抓包 - 推荐）

### 1、启动 getAppToken 程序
运行 `getAppToken.exe` 或 `python getAppToken.py`

### 2、选择 Steam 模式
```
选择获取哪个App的token:
1、悠悠有品
2、BUFF
3、Steam (浏览器)
-------------------

请输入数字: 3
```

### 3、管理员权限（自动请求）
- **Windows**: 程序会自动弹出 UAC 提示，点击"是"即可
- **Linux/Mac**: 需要手动使用 `sudo` 运行

### 4、程序自动监控网卡
程序会自动监控本地网卡的网络流量，无需任何手动配置。

### 5、访问 Steam（HTTP 页面）
在浏览器中访问：
- `http://steamcommunity.com` （注意是 HTTP，不是 HTTPS）
- 或访问任何会产生 HTTP 请求的 Steam 页面

### 6、自动抓取 Cookie
程序会自动检测并提取经过网卡的 Steam Cookie，成功后自动显示并退出。

### 7、查看结果
```
Steam Cookie 获取工具 v3.0 - 网卡监控版
============================================================
Cookie             steamLoginSecure=xxx; sessionid=yyy; ...
============================================================
```

---

## 📖 方法二：手动获取（详细教程）

### Chrome/Edge 浏览器（推荐）

#### 步骤：
1. 打开浏览器，访问：https://steamcommunity.com
2. 登录你的 Steam 账号
3. 按 **F12** 打开开发者工具
4. 切换到 **Application**（应用程序）标签
5. 左侧菜单展开：**Storage** → **Cookies** → **https://steamcommunity.com**
6. 找到以下重要 Cookie：
   - `steamLoginSecure`（最重要）
   - `sessionid`
   - `steamCountry`

#### 快速方法（推荐）：
1. 按 **F12** 打开开发者工具
2. 切换到 **Console**（控制台）标签
3. 输入以下命令并回车：
   ```javascript
   document.cookie
   ```
4. 复制输出的完整 Cookie 字符串

![Chrome获取Cookie示例](../imge/steam/chrome_cookie.png)

---

### Firefox 浏览器

#### 步骤：
1. 访问：https://steamcommunity.com 并登录
2. 按 **F12** 打开开发者工具
3. 切换到 **Storage**（存储）标签
4. 左侧菜单：**Cookies** → **https://steamcommunity.com**
5. 查看并复制所需的 Cookie 值

#### 快速方法：
同样可以在 **Console** 标签中使用 `document.cookie` 命令。

---

### 使用浏览器扩展（最简单）

#### Chrome 扩展：
- **EditThisCookie**
- **Cookie-Editor**

#### Firefox 扩展：
- **Cookie Quick Manager**

#### 使用步骤：
1. 安装上述任一扩展
2. 访问 Steam 社区并登录
3. 点击扩展图标
4. 选择导出所有 Cookie
5. 选择 **JSON** 或 **Netscape** 格式

---

## 📝 Cookie 格式说明

### 完整格式（推荐）：
```
steamLoginSecure=76561198xxxxx%7C%7Cxxxx; sessionid=xxxxxxxx; steamCountry=CN; timezoneOffset=28800,0
```

### 单独字段格式：
```
steamLoginSecure: 76561198xxxxx%7C%7Cxxxx
sessionid: xxxxxxxxxxxxxxxx
steamCountry: CN
```

---

## 🔑 重要的 Cookie 字段

| 字段名 | 说明 | 必需性 |
|--------|------|--------|
| `steamLoginSecure` | Steam 登录令牌 | ✅ 必需（最重要） |
| `sessionid` | 会话 ID | ✅ 必需 |
| `steamCountry` | 国家/地区代码 | 📌 建议 |
| `timezoneOffset` | 时区偏移 | ⚪ 可选 |

---

## ⚠️ 安全提示

1. **Cookie 包含登录凭证**，请妥善保管
2. **不要分享给他人**，避免账号被盗
3. **Cookie 有时效性**，过期后需重新获取
4. **建议定期更新**，保持 Cookie 有效性
5. **使用完毕后**，建议退出 Steam 登录

---

## 🐛 常见问题

### Q1: Cookie 中没有 steamLoginSecure 字段？
**A:** 请确保你已经登录 Steam。未登录状态下无法获取此字段。

### Q2: Cookie 获取后无法使用？
**A:** Cookie 可能已过期。请重新登录 Steam 并获取新的 Cookie。

### Q3: 复制的 Cookie 太长怎么办？
**A:** 这是正常的。Steam Cookie 通常包含多个字段，完整复制即可。

### Q4: 需要获取哪个页面的 Cookie？
**A:** 
- 个人资料页面：`https://steamcommunity.com/profiles/`
- 市场页面：`https://steamcommunity.com/market/`
- 通常两个页面的 Cookie 是相同的

### Q5: 使用 document.cookie 获取不完整？
**A:** 某些 HTTPOnly Cookie 无法通过 JavaScript 获取。建议使用开发者工具的 Application/Storage 标签查看。

---

## 💡 使用建议

1. **首选方法**：Chrome 开发者工具 + Console（最快）
2. **次选方法**：浏览器扩展（最方便）
3. **备用方法**：Application 标签手动查看（最详细）

---

## 📞 需要帮助？

如果遇到问题，请使用 getAppToken 工具的选项 1，查看详细的获取教程。
