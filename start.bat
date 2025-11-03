@echo off
chcp 65001 >nul

setlocal

call conda activate CS2DB

cd /d "%~dp0blankEndApi"
start /b cmd /c "python blankEndApi.py"

cd /d "%~dp0Spider"
start /b cmd /c "python Spider.py"

cd /d "%~dp0WebSite"
if exist "package.json" (
    start /b cmd /c "npm run serve"
)
cd /d "%~dp0"

pause