@echo off
chcp 65001 >nul

setlocal

call conda activate CS2DB

cd /d "%~dp0backEnd"
start /b cmd /c "python backEnd.py"

cd /d "%~dp0Spider"
start /b cmd /c "python Spider.py"

cd /d "%~dp0WebSite"
if exist "package.json" (
    call npm install
    start /b cmd /c "cd /d %~dp0WebSite && npm run dev"
)

cd /d "%~dp0"
pause