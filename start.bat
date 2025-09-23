@echo off
chcp 65001 >nul

call conda activate CS2DB

:: 启动各个服务，每个服务都从项目根目录开始
start /b cmd /c "cd blankEndApi && python blankEndApi.py"
timeout /t 1 /nobreak >nul

start /b cmd /c "cd Spider && python Spider.py"
timeout /t 1 /nobreak >nul

if exist "WebSite\package.json" (
    start /b cmd /c "cd WebSite && npm run serve"
)

:: 保持窗口打开，显示所有输出
pause