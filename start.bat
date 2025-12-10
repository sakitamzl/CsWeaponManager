@echo off
chcp 65001 >nul

setlocal

call conda activate CS2DB

cd /d "%~dp0backEnd"
start "后端服务" cmd /c "python backEnd.py"

cd /d "%~dp0Spider"
start "Spider服务" cmd /c "python Spider.py"

cd /d "%~dp0WebSite"
if exist "package.json" (
    start "前端服务" cmd /c "npm run dev"
)

cd /d "%~dp0"
pause