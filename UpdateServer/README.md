# UpdateServer - C# 版本更新服务器

基于 .NET 8.0 开发的跨平台更新服务器，支持 Windows 和 Linux。

## 快速开始

### 1. 安装 .NET 8.0 SDK

下载地址: https://dotnet.microsoft.com/download/dotnet/8.0

### 2. 打包

**一键打包（Windows + Linux 同时构建）**：
```bash
build_all.bat
```

**只打包 Windows 版本**：
```bash
build_windows.bat
```

**只打包 Linux 版本**：
```bash
build_linux.bat
```

### 3. 运行

**Windows**：
```bash
cd release_win
UpdateServer.exe
```

**Linux**：
```bash
cd release_linux
chmod +x UpdateServer
./UpdateServer
```

## 目录结构

```
UpdateServer/
├── Program.cs              # 主程序
├── UpdateServer.csproj     # 项目配置
├── appsettings.json        # 配置文件
├── build_all.bat           # 一键打包脚本
├── build_windows.bat       # Windows 打包脚本
├── build_linux.bat         # Linux 打包脚本
└── Releases/               # 版本目录
    └── v2.3.6/
        ├── update.zip      # 更新包
        └── version.json    # 版本信息
```

## API 接口

- `GET /health` - 健康检查
- `GET /api/update/check?currentVersion=2.3.5` - 检查更新
- `GET /api/update/download` - 下载更新包
- `GET /api/update/versions` - 列出所有版本

## 版本管理

在 `Releases/` 目录下创建版本文件夹（格式：vX.Y.Z），包含：

1. **update.zip** - 更新包（必需）
2. **version.json** - 版本信息（可选）

version.json 示例：
```json
{
  "version": "v2.3.6",
  "release_date": "2026-02-10",
  "description": "版本描述",
  "required": false,
  "changelog": [
    "新增：xxx功能",
    "优化：xxx逻辑",
    "修复：xxx问题"
  ]
}
```

## Linux 部署

### 方法1：直接运行
```bash
# 上传文件
scp -r release_linux user@makurochan.com:/opt/updateserver/

# 运行
cd /opt/updateserver
chmod +x UpdateServer
./UpdateServer
```

### 方法2：配置为系统服务
```bash
# 复制服务文件（打包时会自动生成）
sudo cp updateserver.service /etc/systemd/system/

# 修改配置
sudo nano /etc/systemd/system/updateserver.service

# 启动服务
sudo systemctl daemon-reload
sudo systemctl start updateserver
sudo systemctl enable updateserver
```

### 防火墙
```bash
# Ubuntu/Debian
sudo ufw allow 9004/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=9004/tcp
sudo firewall-cmd --reload
```

## 配置

编辑 `appsettings.json` 修改端口等配置：
```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://0.0.0.0:9004"
      }
    }
  }
}
```
