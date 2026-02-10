@echo off
chcp 65001 > nul
title UpdateServer 一键打包（Windows + Linux）

echo ============================================================
echo   UpdateServer 一键打包工具
echo   同时构建 Windows 和 Linux 版本
echo ============================================================
echo.

REM 检查 .NET SDK
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

REM 清理所有旧文件
echo 🧹 清理所有旧文件...
if exist publish_win rmdir /s /q publish_win
if exist publish_linux rmdir /s /q publish_linux
if exist release_win rmdir /s /q release_win
if exist release_linux rmdir /s /q release_linux
echo ✅ 清理完成
echo.

echo ============================================================
echo   第一步：构建 Windows 版本
echo ============================================================
echo.

dotnet publish UpdateServer.csproj ^
    -c Release ^
    -r win-x64 ^
    --self-contained true ^
    -p:PublishSingleFile=true ^
    -p:IncludeNativeLibrariesForSelfExtract=true ^
    -p:EnableCompressionInSingleFile=true ^
    -o publish_win

if %errorlevel% neq 0 (
    echo ❌ Windows 版本构建失败
    pause
    exit /b 1
)

echo ✅ Windows 版本构建完成
echo.

echo ============================================================
echo   第二步：构建 Linux 版本
echo ============================================================
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

echo ============================================================
echo   第三步：创建发布目录
echo ============================================================
echo.

REM 创建 Windows 发布目录
echo 📦 创建 Windows 发布目录...
mkdir release_win
copy publish_win\UpdateServer.exe release_win\
copy appsettings.json release_win\
mkdir release_win\Releases
if exist Releases\v2.3.6 xcopy /E /I /Y Releases\v2.3.6 release_win\Releases\v2.3.6
echo ✅ Windows 发布目录完成
echo.

REM 创建 Linux 发布目录
echo 📦 创建 Linux 发布目录...
mkdir release_linux
copy publish_linux\UpdateServer release_linux\
copy appsettings.json release_linux\
mkdir release_linux\Releases
if exist Releases\v2.3.6 xcopy /E /I /Y Releases\v2.3.6 release_linux\Releases\v2.3.6

REM 创建 Linux 启动脚本
(
echo #!/bin/bash
echo SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo cd "$SCRIPT_DIR"
echo chmod +x UpdateServer
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
echo.
echo [Install]
echo WantedBy=multi-user.target
) > release_linux\updateserver.service

echo ✅ Linux 发布目录完成
echo.

echo ============================================================
echo   打包完成！
echo ============================================================
echo.
echo ✅ Windows 版本:
echo    📁 release_win\UpdateServer.exe
echo    💾 大小:
dir /b release_win\UpdateServer.exe | xargs -I {} cmd /c "dir {}"
echo.
echo ✅ Linux 版本:
echo    📁 release_linux\UpdateServer
echo    💾 大小:
dir /b release_linux\UpdateServer
echo.
echo 使用方法:
echo.
echo  【Windows】
echo    1. 进入 release_win 目录
echo    2. 双击 UpdateServer.exe 运行
echo.
echo  【Linux】
echo    1. 上传: scp -r release_linux user@makurochan.com:/opt/updateserver/
echo    2. 赋权: chmod +x UpdateServer
echo    3. 运行: ./UpdateServer
echo.

pause
