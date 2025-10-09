# Steam长效令牌使用说明

## 📋 概述

Steam现在支持使用长效令牌（`steamLoginSecure` 和 `steamRefresh_steam`）来访问库存API，无需频繁重新登录。

## 🔑 关键Cookie说明

### 1. steamLoginSecure
- **格式**: `76561198334278515||eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0...`
- **作用**: 主要的认证令牌，包含用户身份和JWT token
- **有效期**: 通常30-90天
- **结构**: `SteamID||JWT_TOKEN`

### 2. steamRefresh_steam
- **作用**: 刷新令牌，用于在主令牌过期时自动获取新的令牌
- **有效期**: 通常更长，可达数月

### 3. 其他重要Cookie

```
browserid - 浏览器标识
sessionid - 会话ID
timezoneOffset - 时区偏移
Steam_Language - Steam语言设置（如：schinese）
steamCountry - Steam国家/地区设置
webTradeEligibility - 交易资格信息
```

## 📝 完整Cookie示例

```
browserid=3501078876096867604; 
timezoneOffset=32400,0; 
recentlyVisitedAppHubs=1063420; 
sessionid=32df64a3a3b1f6ea19d34cf5; 
webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22%3A1753180411%7D; 
app_impressions=928520@2_groupannouncements_detail_|550@2_100100_100101_100105|550@2_100100_100101_100103|730@2_100100_100101_100106|730@2_100100_100101_100106; 
Steam_Language=schinese; 
strInventoryLastContext=730_0; 
steamCountry=JP%7C93152bf2aa03408ebd28bd2fa40b4ec9; 
steamLoginSecure=76561198334278515%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MDAwNV8yNjIwNkNFRV9CRDA5MSIsICJzdWIiOiAiNzY1NjExOTgzMzQyNzg1MTUiLCAiYXVkIjogWyAid2ViOmNvbW11bml0eSIgXSwgImV4cCI6IDE3NjAwMzg0NDksICJuYmYiOiAxNzUxMzExODQ2LCAiaWF0IjogMTc1OTk1MTg0NiwgImp0aSI6ICIwMDBEXzI3MEYzODNFX0NEM0YxIiwgIm9hdCI6IDE3NDQ1NTA4MDYsICJydF9leHAiOiAxNzYyNDk3NzE2LCAicGVyIjogMCwgImlwX3N1YmplY3QiOiAiMTI2LjUxLjE4OC41MyIsICJpcF9jb25maXJtZXIiOiAiMTI2LjUxLjE4OC41MyIgfQ.PBmmWHU7ft1QMwPOUq5H9u-NaOi3GPT_6LJXRINsGtkIjStIxCPtVTxjkBBc2rVeWJTnj3yWwF7Xxrd-B-HDAw
```

## 🔧 技术实现

### 修改的文件
`Spider/src/web_site/Steam/steam_Inventory.py`

### 主要更新

#### 1. Cookie自动补全功能 ⭐ NEW

系统会自动补全缺失的Cookie字段，即使您只提供 `steamLoginSecure`，系统也会自动添加其他必要字段：

**自动补全的字段**:
```python
default_fields = {
    'timezoneOffset': '自动检测系统时区',    # 时区偏移（智能获取）⭐
    'browserid': '随机生成19位数字',        # 浏览器ID
    'recentlyVisitedAppHubs': '730',       # CS2 AppID
    'Steam_Language': 'schinese',          # 简体中文
    'strInventoryLastContext': '730_2',    # 库存上下文
    'steamCountry': 'CN%7C0',              # 国家/地区
    'app_impressions': '730@2_...',        # 应用印象
    'webTradeEligibility': '{...}',        # 交易资格（JSON格式）
    'sessionid': '随机生成24位十六进制'     # 会话ID
}
```

**时区自动检测** ⭐:
- 自动读取Windows系统时区设置
- 支持夏令时自动识别
- 格式：`秒数,是否夏令时` 例如：
  - UTC+8 (北京): `28800,0`
  - UTC+9 (东京): `32400,0`
  - UTC-5 (纽约): `-18000,0`
  - UTC-7 夏令时: `-25200,1`

**使用示例**:
```python
# 输入：只有核心令牌
cookie = "steamLoginSecure=76561198334278515||eyAidHlwIjog..."

# 输出：自动补全为完整Cookie
complete_cookie = """
browserid=3501078876096867604; 
timezoneOffset=32400,0; 
recentlyVisitedAppHubs=730; 
sessionid=自动生成; 
webTradeEligibility=%7B%22allowed%22%3A1%2C...%7D; 
app_impressions=730@2_100100_100101_100106; 
Steam_Language=schinese; 
strInventoryLastContext=730_2; 
steamCountry=CN%7C0; 
steamLoginSecure=76561198334278515||eyAidHlwIjog...
"""
```

**日志输出示例**:
```
补全Cookie字段: timezoneOffset=32400,0
补全Cookie字段: browserid=3501078876096867604
补全Cookie字段: Steam_Language=schinese
原始Cookie长度: 450 字符
补全后Cookie长度: 892 字符
```

#### 2. 增强的HTTP请求头
```python
self.setam_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': f'https://steamcommunity.com/profiles/{self.steamId}/inventory/',
    'Origin': 'https://steamcommunity.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': self.steam_cookie  # 完整的Cookie字符串
}
```

#### 2. 改进的错误处理
```python
def getsteamInventory(self, url):
    """
    获取Steam库存数据
    支持使用steamLoginSecure长效令牌和steamRefresh_steam刷新令牌
    """
    try:
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 发送请求
        req = requests.get(url, headers=self.setam_headers, verify=False, timeout=30)
        
        # 检查响应状态码
        if req.status_code == 200:
            weaponJSON = req.json()
            return weaponJSON
        elif req.status_code == 401:
            # Cookie已过期
            return None
        elif req.status_code == 403:
            # 访问被拒绝（库存隐私设置）
            return None
        # ...
    except Exception as e:
        # 错误处理
        return None
```

#### 3. 详细的日志记录
- 初始化时记录SteamID和Cookie长度
- 每次请求记录URL
- 成功时记录状态码
- 失败时记录详细错误信息

## 🎯 使用方法

### 1. 获取完整Cookie

#### 方式一：使用Steam二维码登录（推荐）
1. 在数据源管理中选择"Steam市场"
2. 选择"扫码登录"
3. 使用Steam APP扫码
4. 系统自动获取包含长效令牌的Cookie

#### 方式二：手动从浏览器复制
1. 登录 `https://steamcommunity.com`
2. 打开浏览器开发者工具（F12）
3. 切换到"网络"（Network）标签页
4. 访问库存页面：`https://steamcommunity.com/profiles/{你的SteamID}/inventory/`
5. 找到任意请求，查看请求头中的Cookie
6. 复制完整的Cookie字符串

### 2. 配置数据源

#### 新增Steam数据源
```
1. 数据源类型: Steam市场
2. Cookie获取方式: 
   - 扫码登录（推荐）- 自动获取长效令牌
   - 手动输入 - 粘贴完整Cookie字符串
3. 填写SteamID
4. 选择更新频率
5. 提交
```

#### 编辑已有数据源
```
1. 打开编辑对话框
2. 选择Cookie获取方式
3. 重新获取或更新Cookie
4. 保存
```

## 📊 API访问的URL

### 库存API端点

#### Context ID = 16 (装饰品)
```
https://steamcommunity.com/inventory/{steamId}/730/16?l=schinese&count=2000
```

#### Context ID = 2 (游戏物品)
```
https://steamcommunity.com/inventory/{steamId}/730/2?l=schinese&count=2000
```

### 参数说明
- `{steamId}`: Steam用户ID（64位）
- `730`: CS2游戏APPID
- `16` / `2`: 上下文ID（不同类型的物品）
- `l=schinese`: 语言设置（简体中文）
- `count=2000`: 每次获取的物品数量

## ⚠️ 注意事项

### 1. Cookie安全性
- ⚠️ **切勿公开分享Cookie**
- ⚠️ Cookie包含完整的账户访问权限
- ✅ 定期更换Cookie
- ✅ 使用HTTPS传输
- ✅ 在安全的网络环境下使用

### 2. Cookie有效期
- `steamLoginSecure`: 通常30-90天
- `steamRefresh_steam`: 通常更长
- 过期后需要重新登录获取

### 3. 状态码说明

| 状态码 | 含义 | 解决方案 |
|--------|------|----------|
| 200 | 成功 | 正常 ✅ |
| 401 | 认证失败 | Cookie已过期，需重新登录 |
| 403 | 访问被拒绝 | 检查库存隐私设置或Cookie |
| 429 | 请求过于频繁 | 减少请求频率，稍后重试 |
| 500 | Steam服务器错误 | Steam服务器问题，稍后重试 |

### 4. 库存隐私设置
确保Steam账户的库存隐私设置为：
- ✅ 公开
- ✅ 或"仅好友可见"（使用自己的Cookie访问）

设置路径：
```
Steam → 个人资料 → 编辑个人资料 → 隐私设置 → 我的个人资料 → 库存
```

## 🔄 Cookie刷新策略

### 自动刷新（推荐）
使用 `steamRefresh_steam` 令牌，系统会自动刷新Cookie。

### 手动刷新
1. 当收到401错误时
2. 定期检查Cookie有效期
3. 使用扫码登录快速获取新Cookie

## 🐛 故障排除

### 问题1: 401 认证失败
**原因**: Cookie已过期或无效

**解决方案**:
1. 重新扫码登录
2. 或手动复制新的Cookie
3. 更新数据源配置

### 问题2: 403 访问被拒绝
**原因**: 
- 库存隐私设置为私密
- Cookie不完整
- IP地址变化触发安全验证

**解决方案**:
1. 检查库存隐私设置
2. 确保Cookie完整（包含所有必要字段）
3. 使用稳定的网络环境

### 问题3: 获取到的库存为空
**原因**:
- API返回空数据
- Context ID不正确
- 账户确实没有库存

**解决方案**:
1. 检查日志中的API响应
2. 确认账户确有CS2库存
3. 尝试在浏览器中手动访问库存URL

### 问题4: 请求超时
**原因**:
- 网络连接问题
- Steam服务器响应慢
- 库存物品过多

**解决方案**:
1. 检查网络连接
2. 增加超时时间（当前为30秒）
3. 稍后重试

## 📈 性能优化建议

### 1. 请求频率控制
```python
# 建议间隔
- 同一用户: 最小间隔30秒
- 不同用户: 可并发，但总QPS不超过10
```

### 2. 数据缓存
```python
# 库存数据通常不会频繁变化
- 缓存时间: 15-30分钟
- 仅在必要时刷新
```

### 3. 批量处理
```python
# 已实现的批量提交
- 一次性获取两个Context ID的数据
- 批量提交到后端API
- 减少数据库操作次数
```

## 📚 相关文档

- [Steam登录功能使用说明](./Steam登录功能使用说明.md)
- [Steam二维码登录使用说明](./Steam二维码登录使用说明.md)
- [Steam数据源统一说明](./Steam数据源统一说明.md)
- [Steam库存更新接口说明](./Steam库存更新接口说明.md)

## 🔗 Steam官方文档

- [Steam Web API](https://steamcommunity.com/dev)
- [Steam Inventory Service](https://partner.steamgames.com/doc/features/inventory)

## 📝 更新日志

### v1.0.4 (2025-10-09)
- ✅ 支持Steam长效令牌（steamLoginSecure）
- ✅ 支持刷新令牌（steamRefresh_steam）
- ✅ **Cookie自动补全功能** ⭐ NEW
  - 自动补全 `timezoneOffset`、`browserid`、`sessionid` 等字段
  - 智能生成 `webTradeEligibility` 交易资格
  - 支持仅提供核心令牌，系统自动补全其他字段
- ✅ 增强HTTP请求头，提高兼容性
- ✅ 改进错误处理和日志记录
- ✅ 添加详细的状态码检查
- ✅ 优化Cookie处理逻辑
- ✅ 详细的调试日志输出

---

**注意**: 本文档随系统更新持续维护。如有问题，请查看日志文件或联系技术支持。

