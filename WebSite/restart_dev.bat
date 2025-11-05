@echo off
echo Cleaning cache and restarting dev server...
cd /d "%~dp0"

REM Kill any existing node processes on port 9003
for /f "tokens=5" %%a in ('netstat -ano ^| find ":9003" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Clean cache
if exist "node_modules\.cache" (
    echo Removing cache...
    rmdir /s /q "node_modules\.cache"
)

REM Start dev server
echo Starting dev server...
npm run serve

