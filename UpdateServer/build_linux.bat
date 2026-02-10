@echo off
chcp 65001 > nul
title UpdateServer Linux 打包工具

echo ============================================================
echo   UpdateServer Linux 打包工具（在 Windows 环境下）
echo ============================================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查项目文件是否存在
if not exist UpdateServer.csproj (
    echo ❌ 错误：未找到 UpdateServer.csproj
    echo    请确保在 UpdateServer 目录下运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ 找到项目文件
echo.

REM 检查 .NET SDK 是否安装
dotnet --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到 .NET SDK，请先安装 .NET 8.0 SDK
    echo.
    echo 下载地址: https://dotnet.microsoft.com/download/dotnet/8.0
    echo.
    pause
    exit /b 1
)

echo ✅ .NET SDK 已安装
dotnet --version
echo.

REM 清理旧的发布文件
echo 🧹 清理旧的发布文件...
if exist publish_linux rmdir /s /q publish_linux
echo ✅ 清理完成
echo.

REM 构建 Linux x64 版本
echo 🔨 开始构建 Linux x64 版本（交叉编译）...
echo.
echo 提示：Windows 下交叉编译 Linux 程序
echo.

dotnet publish UpdateServer.csproj ^
    -c Release ^
    -r linux-x64 ^
    --self-contained true ^
    -p:PublishSingleFile=true ^
    -p:IncludeNativeLibrariesForSelfExtract=true ^
    -p:EnableCompressionInSingleFile=true ^
    -o publish_linux

if %errorlevel% neq 0 (
    echo ❌ Linux 版本构建失败
    pause
    exit /b 1
)

echo ✅ Linux 版本构建完成
echo.

REM 检查生成的文件
if exist publish_linux\UpdateServer (
    echo ✅ Linux 可执行文件生成成功！
    echo 📁 位置: publish_linux\UpdateServer
    dir publish_linux\UpdateServer
    echo.

    REM 创建发布目录
    echo 📦 创建 Linux 发布目录...
    if not exist release_linux mkdir release_linux
    copy publish_linux\UpdateServer release_linux\
    copy appsettings.json release_linux\
    if not exist release_linux\Releases mkdir release_linux\Releases
    if exist Releases\v2.3.6 xcopy /E /I /Y Releases\v2.3.6 release_linux\Releases\v2.3.6

    REM 创建启动脚本
    (
    echo #!/bin/bash
    echo # UpdateServer 启动脚本
    echo.
    echo SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo cd "$SCRIPT_DIR"
    echo.
    echo echo "============================================================"
    echo echo "  CS Weapon Manager - 更新服务器"
    echo echo "============================================================"
    echo echo ""
    echo.
    echo # 确保有执行权限
    echo chmod +x UpdateServer
    echo.
    echo # 启动服务器
    echo ./UpdateServer
    ) > release_linux\start.sh

    REM 创建 systemd 服务文件
    (
    echo [Unit]
    echo Description=CS Weapon Manager Update Server
    echo After=network.target
    echo.
    echo [Service]
    echo Type=simple
    echo User=your_username
    echo WorkingDirectory=/opt/updateserver
    echo ExecStart=/opt/updateserver/UpdateServer
    echo Restart=always
    echo RestartSec=10
    echo Environment="ASPNETCORE_ENVIRONMENT=Production"
    echo Environment="LANG=zh_CN.UTF-8"
    echo StandardOutput=journal
    echo StandardError=journal
    echo SyslogIdentifier=updateserver
    echo.
    echo [Install]
    echo WantedBy=multi-user.target
    ) > release_linux\updateserver.service

    REM 创建部署说明
    (
    echo # UpdateServer Linux 部署说明
    echo.
    echo ## 上传文件到服务器
    echo ```bash
    echo scp -r release_linux user@makurochan.com:/opt/updateserver/
    echo ```
    echo.
    echo ## 服务器端操作
    echo ```bash
    echo # 登录服务器
    echo ssh user@makurochan.com
    echo.
    echo # 进入目录
    echo cd /opt/updateserver
    echo.
    echo # 赋予执行权限
    echo chmod +x UpdateServer
    echo chmod +x start.sh
    echo.
    echo # 直接运行
    echo ./UpdateServer
    echo.
    echo # 或使用启动脚本
    echo ./start.sh
    echo ```
    echo.
    echo ## 配置为系统服务
    echo ```bash
    echo # 复制服务文件
    echo sudo cp updateserver.service /etc/systemd/system/
    echo.
    echo # 修改服务文件中的用户和路径
    echo sudo nano /etc/systemd/system/updateserver.service
    echo.
    echo # 重载配置
    echo sudo systemctl daemon-reload
    echo.
    echo # 启动服务
    echo sudo systemctl start updateserver
    echo.
    echo # 查看状态
    echo sudo systemctl status updateserver
    echo.
    echo # 开机自启
    echo sudo systemctl enable updateserver
    echo ```
    echo.
    echo ## 防火墙配置
    echo ```bash
    echo # Ubuntu/Debian
    echo sudo ufw allow 9004/tcp
    echo.
    echo # CentOS/RHEL
    echo sudo firewall-cmd --permanent --add-port=9004/tcp
    echo sudo firewall-cmd --reload
    echo ```
    ) > release_linux\DEPLOY.md

    echo ✅ Linux 发布目录创建完成: release_linux\
    echo.
) else (
    echo ❌ 未找到 Linux 可执行文件
)

echo ============================================================
echo   Linux 打包完成！
echo ============================================================
echo.
echo 📁 可执行文件: publish_linux\UpdateServer
echo 📁 发布目录: release_linux\
echo.
echo 部署到 Linux 服务器：
echo   1. 上传: scp -r release_linux user@makurochan.com:/opt/updateserver/
echo   2. 赋权: chmod +x UpdateServer
echo   3. 运行: ./UpdateServer
echo.
echo 详细部署说明请查看: release_linux\DEPLOY.md
echo.

pause
