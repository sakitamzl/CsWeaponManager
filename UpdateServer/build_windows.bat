@echo off
chcp 65001 > nul
title UpdateServer Windows 打包工具

echo ============================================================
echo   UpdateServer Windows 打包工具
echo ============================================================
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
if exist publish_win rmdir /s /q publish_win
if exist publish_linux rmdir /s /q publish_linux
echo ✅ 清理完成
echo.

REM 构建 Windows 版本
echo 🔨 开始构建 Windows x64 版本...
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

REM 检查生成的文件
if exist publish_win\UpdateServer.exe (
    echo ✅ Windows 可执行文件生成成功！
    echo 📁 位置: publish_win\UpdateServer.exe
    dir publish_win\UpdateServer.exe
    echo.

    REM 创建发布目录
    echo 📦 创建 Windows 发布目录...
    if not exist release_win mkdir release_win
    copy publish_win\UpdateServer.exe release_win\
    copy appsettings.json release_win\
    if not exist release_win\Releases mkdir release_win\Releases
    if exist Releases\v2.3.6 xcopy /E /I /Y Releases\v2.3.6 release_win\Releases\v2.3.6

    echo ✅ Windows 发布目录创建完成: release_win\
    echo.
) else (
    echo ❌ 未找到 Windows 可执行文件
)

echo ============================================================
echo   Windows 打包完成！
echo ============================================================
echo.
echo 📁 可执行文件: publish_win\UpdateServer.exe
echo 📁 发布目录: release_win\
echo.
echo 运行方法:
echo   cd release_win
echo   UpdateServer.exe
echo.

pause
