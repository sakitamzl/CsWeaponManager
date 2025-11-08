# CS武器管理器 (CS Weapon Manager)

> 一个功能完善的CS2/CSGO饰品交易管理系统，帮助您高效管理Steam饰品的购买、出售、租赁等操作。

## 📋 项目简介

CS武器管理器是一个集成了多个交易平台的饰品管理系统，支持对Steam库存中的CS2/CSGO饰品进行统一管理和跨平台价格对比。系统采用前后端分离架构，提供直观的Web界面和强大的后端API支持。

## ⚠️ 重要声明

**本项目仅供学习交流使用，请勿用于商业用途。**

**关于Spider模块说明**：
- Spider爬虫模块涉及APK解包和逆向工程相关技术
- 根据《中华人民共和国数据安全法》和《中华人民共和国个人信息保护法》的相关规定
- Spider模块**不予开源**，仅在本地保留用于个人学习研究
- 本项目开源部分为饰品管理系统的核心功能，不包含任何爬虫或数据采集功能

## ✨ 主要功能

### 🎯 核心功能
- **库存管理** - 实时同步和查看Steam库存饰品
- **购买记录** - 记录和追踪饰品购买信息
- **出售管理** - 管理饰品出售记录和收益
- **租赁系统** - 支持饰品租赁功能
- **价格对比** - 多平台价格实时对比（悠悠有品、BUFF、Steam）
- **数据统计** - 可视化展示交易数据和收益分析
- **库存组件** - Steam库存历史记录查询

### 🔌 支持平台
- **Steam市场** - Steam官方市场集成
- **悠悠有品 (youpin898)** - 国内主流交易平台
- **BUFF163** - 网易BUFF饰品交易平台
- **完美世界** - 完美世界平台支持

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **Node.js**: 14.0+
- **数据库**: SQLite (自动创建)
- **conda** (推荐用于Python环境管理)

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/yourusername/CsWeaponManager.git
cd CsWeaponManager
```

#### 2. 后端配置

```bash
# 创建并激活conda环境
conda create -n CS2DB python=3.8
conda activate CS2DB

# 安装后端依赖（根据项目需要）
cd blankEndApi
pip install flask flask-cors
# 其他依赖根据实际情况安装
```

#### 3. 前端配置

```bash
# 进入前端目录
cd WebSite

# 安装依赖
npm install
```

#### 4. 配置文件

编辑 `blankEndApi/conf.ini` 配置文件：

```ini
[database]
sqlite_file = csweaponmanager.db

[http_proxy]
true = True
host = 127.0.0.1
port = 10811

[socks5]
host = 127.0.0.1
port = 10808

[LogLevel]
level = error
sometime = 14

[processes]
number = 1
```

### 运行项目

#### 开发环境运行

使用启动脚本一键启动所有服务：

```bash
start.bat
```

或手动分别启动：

```bash
# 1. 启动后端API服务
cd backEndApi
python backEndApi.py
# 服务将运行在 http://0.0.0.0:9001

# 2. 启动前端服务（新终端）
cd WebSite
npm run serve
# 前端将运行在 http://localhost:8080
```

#### 生产环境部署

使用PyInstaller打包后的可执行文件：

```bash
# 进入发布目录
cd Releases\v1.1.5

# 运行启动脚本
start_all.bat
```

访问地址：`http://localhost:9003`

## 📁 项目结构

```
CsWeaponManager/
├── blankEndApi/              # 后端API服务
│   ├── blankEndApi.py       # 主入口文件
│   ├── conf.ini             # 配置文件
│   ├── csweaponmanager.db   # SQLite数据库
│   └── src/                 # 源代码目录
│       ├── config/          # 配置模块
│       ├── db_manager/      # 数据库管理
│       │   ├── buff/       # BUFF平台数据模型
│       │   ├── steam/      # Steam平台数据模型
│       │   ├── yyyp/       # 悠悠有品数据模型
│       │   └── index/      # 核心数据模型
│       └── web_side/        # Web接口路由
│           ├── buff163/     # BUFF API
│           ├── steam/       # Steam API
│           ├── youpin898/   # 悠悠有品 API
│           └── webSide/     # 前端接口
├── WebSite/                 # 前端Vue3项目
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   │   ├── Home.vue           # 主页（数据统计）
│   │   │   ├── Buy.vue            # 购买管理
│   │   │   ├── Sell.vue           # 出售管理
│   │   │   ├── Lent.vue           # 租赁管理
│   │   │   ├── Inventory.vue      # 库存查看
│   │   │   ├── DataSource.vue     # 数据源配置
│   │   │   ├── SteamMarket.vue    # Steam市场
│   │   │   └── Setting.vue        # 系统设置
│   │   ├── router/         # 路由配置
│   │   └── config/         # API配置
│   └── package.json        # 项目依赖
├── Releases/                # 发布版本
└── start.bat               # 开发环境启动脚本
```

## 🎨 功能模块

### 主页 (Home)
- 总购买金额统计
- 总出售金额统计
- 总库存数量
- 多平台价格对比
- 收益差价分析

### 购买管理 (Buy)
- 记录饰品购买信息
- 多平台购买记录
- 购买历史查询

### 出售管理 (Sell)
- 饰品出售记录
- 收益统计
- 出售历史追踪

### 租赁管理 (Lent)
- 饰品租赁功能
- 租赁记录管理

### 库存查看 (Inventory)
- Steam库存实时同步
- 饰品详情展示
- 价格追踪

### 数据源配置 (DataSource)
- 平台Cookie配置
- API密钥管理

## 🔧 API接口

后端API服务运行在 `http://localhost:9001`

### 主要接口路由

- `/configV1/*` - 系统配置
- `/youpin898BuyV1/*` - 悠悠有品购买
- `/youpin898SellV1/*` - 悠悠有品出售
- `/youpin898LentV1/*` - 悠悠有品租赁
- `/buff163BuyV1/*` - BUFF购买
- `/buff163SellV1/*` - BUFF出售
- `/steamMarketV1/*` - Steam市场
- `/steamInventoryV1/*` - Steam库存
- `/webInventoryV1/*` - 库存管理接口
- `/indexPage/*` - 首页数据接口

## 📦 打包发布

使用提供的打包脚本：

```bash
pyinstaller.bat
```

脚本会自动：
1. 激活conda环境
2. 清理旧的构建文件
3. 打包后端API为 `blankEndApi.exe`
4. 复制必要配置文件
5. 创建发布目录 `Releases/v1.x.x/`

## 📝 配置说明

### 代理设置
系统支持HTTP和SOCKS5代理，用于访问Steam等国际平台：

```ini
[http_proxy]
true = True
host = 127.0.0.1
port = 10811

[socks5]
host = 127.0.0.1
port = 10808
```

### 日志配置
```ini
[LogLevel]
level = error        # 日志级别: debug/info/warning/error
sometime = 14        # 日志保留天数
```

## 🔐 ADB与网络证书安装

本项目提供了自动化的网络抓包证书安装功能，支持在MuMu模拟器等Android设备上安装系统证书。

### 快速开始

1. **开启MuMu模拟器"可选系统盘"功能**（必需）
2. 访问 `http://localhost:9003` 的 **"开发工具"** 页面
3. 扫描并连接设备
4. 点击 **"安装证书"** 按钮
5. 重启模拟器使证书生效

### 详细文档

完整的安装指南、故障排查和技术说明，请参阅：

📖 **[ADB与网络证书安装完整文档](doc/ADB与网络证书安装.md)**

文档包含：
- ✅ 详细的安装步骤
- ✅ MuMu模拟器配置方法
- ✅ 常见问题排查（5个常见问题）
- ✅ 手动安装方法（备用方案）
- ✅ 技术原理说明
- ✅ 安全提示和注意事项

### 核心功能

- **自动安装** - Web界面一键安装，无需手动执行命令
- **智能检测** - 自动检测设备信息和证书状态
- **多设备支持** - 支持MuMu模拟器及其他已root的Android设备
- **证书管理** - 支持安装、卸载、状态查询
- **详细日志** - 完整的操作日志便于故障排查

## 🛠️ 技术栈

### 后端
- **Flask** - Web框架
- **SQLite** - 数据库
- **Flask-CORS** - 跨域支持

### 前端
- **Vue 3** - 前端框架
- **Vue Router 4** - 路由管理
- **Axios** - HTTP客户端
- **Element Plus** - UI组件库

## 📊 数据库

项目使用SQLite数据库，主要数据表包括：

- 购买记录表 (buy)
- 出售记录表 (sell)
- 租赁记录表 (lease)
- 库存表 (steam_inventory)
- 价格记录表 (buff/yyyp)
- 配置表 (config)

## ⚠️ 注意事项

1. **Cookie配置**: 需要在数据源页面配置各平台的Cookie才能正常使用
2. **代理设置**: 访问Steam需要配置代理
3. **数据备份**: 定期备份 `csweaponmanager.db` 数据库文件
4. **日志文件**: 日志文件位于 `blankEndApi/log/` 目录

## 🤝 贡献

欢迎提交Issue和Pull Request！

## ⚖️ 法律声明与免责条款

### 使用声明
1. **本项目仅供个人学习、研究和交流使用**
2. 使用者应遵守当地法律法规及相关平台的服务条款
3. 禁止将本项目用于任何商业用途
4. 禁止利用本项目进行任何违法违规活动

### 免责声明
1. 使用本项目所产生的一切后果由使用者自行承担
2. 开发者不对使用本项目造成的任何损失负责
3. 本项目不保证数据的准确性和完整性
4. 如有侵权，请联系删除

### Spider模块特别说明
- Spider模块涉及APK逆向工程，根据《中华人民共和国数据安全法》《中华人民共和国个人信息保护法》等相关法律法规，**该模块不予开源**
- 本仓库不包含任何爬虫、数据采集相关代码
- 请使用者通过合法途径获取数据

## 📄 许可证

本项目采用学习交流许可，不得用于商业用途。

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- Issues: [项目Issues页面]
- Email: [您的邮箱]

---

⭐ 如果这个项目对您有帮助，欢迎Star支持！

**再次提醒：本项目仅供学习交流，请合法合规使用！**

