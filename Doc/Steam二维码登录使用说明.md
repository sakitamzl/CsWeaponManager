# Steam二维码登录功能使用说明

## 功能概述

现在支持两种Steam登录方式：
1. **扫码登录（推荐）** - 更快速、更安全
2. **账号密码登录** - 传统方式，需要Steam Guard验证码

## 使用步骤

### 方式一：扫码登录（推荐）

1. **打开数据源页面**
   - 点击"新增数据源"按钮
   - 选择数据源类型为"Steam市场(登录)"

2. **选择登录方式**
   - 选择"扫码登录（推荐）"

3. **生成二维码**
   - 点击"生成二维码"按钮
   - 系统会自动生成一个Steam登录二维码

4. **使用Steam手机APP扫码**
   - 打开Steam手机APP
   - 在APP中找到扫码功能
   - 扫描页面上显示的二维码
   - 在手机上确认登录

5. **等待登录成功**
   - 系统会自动检测扫码状态（每2秒检查一次）
   - 扫码成功后，会自动获取Cookie和SteamID
   - 看到"✅ 登录成功"提示后，填写其他必要信息并提交即可

### 方式二：账号密码登录

1. **选择登录方式**
   - 选择"账号密码登录"

2. **填写账号信息**
   - 输入Steam用户名
   - 输入Steam密码
   - 如果启用了Steam Guard，输入5位验证码

3. **点击登录**
   - 点击"立即登录获取Cookie"按钮
   - 等待登录完成

## 技术说明

### 扫码登录原理

1. **生成二维码**
   - 调用Steam官方API `IAuthenticationService/BeginAuthSessionViaQR`
   - 生成包含challenge_url的二维码

2. **轮询状态**
   - 每2秒调用 `IAuthenticationService/PollAuthSessionStatus` 检查状态
   - 等待用户扫码确认

3. **获取凭证**
   - 扫码成功后，获取access_token和refresh_token
   - 转换为session cookies供后续使用

### API接口

#### 1. 生成二维码
```
POST /steamLoginV1/qrcode/generate
响应：
{
  "success": true,
  "data": {
    "session_id": "会话ID",
    "qr_code": "data:image/png;base64,...",
    "interval": 5
  }
}
```

#### 2. 轮询登录状态
```
POST /steamLoginV1/qrcode/poll
请求体：
{
  "session_id": "会话ID"
}

响应（等待中）：
{
  "success": true,
  "status": "waiting"
}

响应（成功）：
{
  "success": true,
  "status": "success",
  "data": {
    "cookies": "Steam cookies",
    "steam_id": "Steam ID",
    "account_name": "账号名"
  }
}
```

## 依赖安装

如果使用二维码登录功能，需要安装额外依赖：

```bash
pip install qrcode[pil]
```

完整依赖列表请查看：`Spider/requirements_steam_login.txt`

## 安全说明

- 二维码会话有效期为5分钟
- 服务器端会自动清理过期的会话
- 建议使用扫码登录，避免直接输入密码
- SSL证书验证已关闭（仅用于开发环境）

## 常见问题

### Q: 二维码一直显示"等待扫码中"？
A: 请检查：
1. 是否使用Steam手机APP扫码
2. 网络连接是否正常
3. 是否在手机上确认了登录

### Q: 提示"二维码已过期"？
A: 二维码有效期为5分钟，请点击"刷新二维码"重新生成

### Q: 扫码成功但没有获取到Cookie？
A: 请查看后端日志（Spider/log/），检查具体错误信息

### Q: 账号密码登录提示"获取RSA密钥失败"？
A: 请检查网络连接，确保能访问steamcommunity.com

## 更新日志

### v1.1.0 (2025-10-09)
- ✅ 新增Steam二维码扫码登录功能
- ✅ 支持两种登录方式切换
- ✅ 自动轮询登录状态
- ✅ 二维码过期自动提示

### v1.0.0 (2025-10-08)
- ✅ 基础账号密码登录功能
- ✅ Steam Guard验证码支持

