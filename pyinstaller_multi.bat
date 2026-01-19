@echo off
echo Starting Multi-Platform PyInstaller packaging process...
echo.

:: Set version number (modify this for each release)
set VERSION=v2.3.2

:: Ask user which platform to build
echo Select build target:
echo [1] Windows only
echo [2] Linux only
echo [3] Both Windows and Linux
echo.
set /p BUILD_TARGET="Enter your choice (1/2/3): "

if "%BUILD_TARGET%"=="1" (
    set BUILD_WINDOWS=1
    set BUILD_LINUX=0
    echo Building for Windows only...
) else if "%BUILD_TARGET%"=="2" (
    set BUILD_WINDOWS=0
    set BUILD_LINUX=1
    echo Building for Linux only...
) else if "%BUILD_TARGET%"=="3" (
    set BUILD_WINDOWS=1
    set BUILD_LINUX=1
    echo Building for both Windows and Linux...
) else (
    echo Invalid choice. Exiting...
    pause
    exit /b 1
)

echo.

:: Sync version to package.json
echo Syncing version to package.json...
set VERSION_NUM=%VERSION%
if "%VERSION_NUM:~0,1%"=="v" set VERSION_NUM=%VERSION_NUM:~1%

set TEMP_PS=%TEMP%\sync_version_temp.ps1
echo $filePath = Resolve-Path 'WebSite\package.json' > "%TEMP_PS%"
echo $content = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8) >> "%TEMP_PS%"
echo $content = $content -replace '^\uFEFF', '' >> "%TEMP_PS%"
echo $oldVersion = 'unknown' >> "%TEMP_PS%"
echo if ($content -match '"version"\s*:\s*"([^"]+)"'^) { $oldVersion = $matches[1] } >> "%TEMP_PS%"
echo $content = [regex]::Replace($content, '"version"\s*:\s*"([^"]+)"', '"version": "%VERSION_NUM%"') >> "%TEMP_PS%"
echo $Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False >> "%TEMP_PS%"
echo [System.IO.File]::WriteAllText($filePath, $content, $Utf8NoBomEncoding) >> "%TEMP_PS%"
echo Write-Host "Version synced: $oldVersion -^> %VERSION_NUM%" >> "%TEMP_PS%"
powershell -NoProfile -ExecutionPolicy Bypass -File %TEMP_PS%
if %errorlevel% neq 0 (
    echo Warning: Failed to sync version to package.json
) else (
    echo Version synced successfully to package.json
)
del %TEMP_PS% >nul 2>&1

:: Activate conda environment
call conda activate CS2DB
if %errorlevel% neq 0 (
    echo Error: Failed to activate conda environment CS2DB
    pause
    exit /b 1
)

:: ================================
:: Build Windows Version
:: ================================
if "%BUILD_WINDOWS%"=="1" (
    echo.
    echo ========================================
    echo Building Windows Version
    echo ========================================

    :: Create Windows release directory
    set WINDOWS_DIR=Releases\%VERSION%\Windows
    if not exist "%WINDOWS_DIR%" mkdir "%WINDOWS_DIR%"
    echo Creating Windows release in: %WINDOWS_DIR%

    :: Clear previous builds
    echo Cleaning previous Windows builds...
    if exist "backEnd\dist" rmdir /s /q "backEnd\dist"
    if exist "backEnd\build" rmdir /s /q "backEnd\build"
    if exist "Spider\dist" rmdir /s /q "Spider\dist"
    if exist "Spider\build" rmdir /s /q "Spider\build"
    if exist "WebServer\dist" rmdir /s /q "WebServer\dist"
    if exist "WebServer\build" rmdir /s /q "WebServer\build"

    :: Package backEnd.py for Windows
    echo.
    echo [Windows 1/3] Packaging backEnd.exe...
    cd backEnd
    pyinstaller --onefile --clean --noconfirm backEnd.py --distpath "..\%WINDOWS_DIR%"
    if %errorlevel% neq 0 (
        echo Error: Failed to package backEnd.py for Windows
        cd ..
        pause
        exit /b 1
    )
    cd ..

    :: Package Spider.py for Windows
    echo.
    echo [Windows 2/3] Packaging Spider.exe...
    cd Spider
    pyinstaller --onefile --clean --noconfirm Spider.py --distpath "..\%WINDOWS_DIR%"
    if %errorlevel% neq 0 (
        echo Error: Failed to package Spider.py for Windows
        cd ..
        pause
        exit /b 1
    )
    cd ..

    :: Package WebServer.py for Windows
    echo.
    echo [Windows 3/3] Packaging WebServer.exe...
    cd WebServer
    pyinstaller --onefile --clean --noconfirm WebServer.py --distpath "..\%WINDOWS_DIR%"
    if %errorlevel% neq 0 (
        echo Error: Failed to package WebServer.py for Windows
        cd ..
        pause
        exit /b 1
    )
    cd ..

    :: Copy additional files for Windows
    echo.
    echo Copying additional files to Windows version folder...
    if exist "Releases\start_all.bat" (
        copy "Releases\start_all.bat" "%WINDOWS_DIR%\start_all.bat"
        echo start_all.bat copied successfully
    )

    if exist "Releases\conf.ini" (
        copy "Releases\conf.ini" "%WINDOWS_DIR%\conf.ini"
        echo conf.ini copied successfully
    )

    :: Copy Documents folder for Windows
    if exist "Documents" (
        echo Copying Documents folder...
        xcopy "Documents" "%WINDOWS_DIR%\Documents\" /E /I /H /Y /Q
        echo Documents folder copied successfully
    )

    :: Create log directory for Windows
    if not exist "%WINDOWS_DIR%\log" mkdir "%WINDOWS_DIR%\log"
    echo log directory created successfully

    echo Windows build completed!
)

:: ================================
:: Build Linux Version
:: ================================
if "%BUILD_LINUX%"=="1" (
    echo.
    echo ========================================
    echo Building Linux Version
    echo ========================================
    echo.
    echo NOTE: Building Linux binaries on Windows requires Docker or WSL2
    echo.

    set LINUX_DIR=Releases\%VERSION%\Linux
    if not exist "%LINUX_DIR%" mkdir "%LINUX_DIR%"
    echo Creating Linux release in: %LINUX_DIR%

    :: Check if Docker is available
    docker --version >nul 2>&1
    if %errorlevel%==0 (
        echo Docker detected. Using Docker to build Linux binaries...
        call :BuildLinuxWithDocker
    ) else (
        :: Check if WSL2 is available
        wsl --status >nul 2>&1
        if %errorlevel%==0 (
            echo WSL2 detected. Using WSL2 to build Linux binaries...
            call :BuildLinuxWithWSL
        ) else (
            echo.
            echo ERROR: Neither Docker nor WSL2 is available.
            echo To build Linux binaries on Windows, you need either:
            echo   1. Docker Desktop installed and running
            echo   2. WSL2 with Python and PyInstaller installed
            echo.
            echo Skipping Linux build...
            set BUILD_LINUX=0
        )
    )
)

:: Build WebSite (common for both platforms)
if exist "WebSite" (
    echo.
    echo ========================================
    echo Building WebSite
    echo ========================================
    cd WebSite

    :: Install dependencies if node_modules doesn't exist
    if not exist "node_modules" (
        echo Installing WebSite dependencies...
        call npm install
        if %errorlevel% neq 0 (
            echo Error: Failed to install WebSite dependencies
            cd ..
            pause
            exit /b 1
        )
    )

    :: Build WebSite
    echo Building WebSite production bundle...
    call npm run build
    if %errorlevel% neq 0 (
        echo Error: Failed to build WebSite
        cd ..
        pause
        exit /b 1
    )

    cd ..

    :: Copy WebSite to Windows version
    if "%BUILD_WINDOWS%"=="1" (
        if exist "WebSite\dist" (
            echo Copying WebSite to Windows version...
            if not exist "%WINDOWS_DIR%\WebSite" mkdir "%WINDOWS_DIR%\WebSite"
            xcopy "WebSite\dist" "%WINDOWS_DIR%\WebSite\dist\" /E /I /H /Y /Q
            echo - WebSite copied to Windows version
        )
    )

    :: Copy WebSite to Linux version
    if "%BUILD_LINUX%"=="1" (
        if exist "WebSite\dist" (
            echo Copying WebSite to Linux version...
            if not exist "%LINUX_DIR%\WebSite" mkdir "%LINUX_DIR%\WebSite"
            xcopy "WebSite\dist" "%LINUX_DIR%\WebSite\dist\" /E /I /H /Y /Q
            echo - WebSite copied to Linux version
        )
    )
)

:: Clean up build artifacts
echo.
echo Cleaning up build artifacts...
if exist "backEnd\build" rmdir /s /q "backEnd\build"
if exist "backEnd\*.spec" del /q "backEnd\*.spec"
if exist "Spider\build" rmdir /s /q "Spider\build"
if exist "Spider\*.spec" del /q "Spider\*.spec"
if exist "WebServer\build" rmdir /s /q "WebServer\build"
if exist "WebServer\*.spec" del /q "WebServer\*.spec"

:: Display results
echo.
echo ========================================
echo Packaging completed successfully!
echo ========================================

if "%BUILD_WINDOWS%"=="1" (
    echo.
    echo Windows executables in: %WINDOWS_DIR%
    dir /b "%WINDOWS_DIR%\*.exe"
)

if "%BUILD_LINUX%"=="1" (
    echo.
    echo Linux binaries in: %LINUX_DIR%
    dir /b "%LINUX_DIR%\" | findstr /V /C:"WebSite" /C:"Documents" /C:"log"
)

echo ========================================

:: Create archives
echo.
echo Creating archives...

if "%BUILD_WINDOWS%"=="1" (
    set ZIP_FILE=Releases\CsWeaponManager_Windows_%VERSION%.zip
    if exist "!ZIP_FILE!" del /q "!ZIP_FILE!"
    echo Compressing Windows version to !ZIP_FILE!...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '%WINDOWS_DIR%\*' -DestinationPath '!ZIP_FILE!' -CompressionLevel Optimal -Force"
    if %errorlevel%==0 (
        echo Windows archive created successfully: !ZIP_FILE!
    )
)

if "%BUILD_LINUX%"=="1" (
    set TAR_FILE=Releases\CsWeaponManager_Linux_%VERSION%.tar.gz
    if exist "!TAR_FILE!" del /q "!TAR_FILE!"
    echo Compressing Linux version to !TAR_FILE!...
    :: Use WSL or Git Bash tar if available
    wsl tar -czf "!TAR_FILE!" -C "%LINUX_DIR%" . 2>nul
    if %errorlevel%==0 (
        echo Linux archive created successfully: !TAR_FILE!
    ) else (
        echo Note: Could not create tar.gz archive. Install WSL or use 7-Zip manually.
    )
)

echo.
echo ========================================
echo All done!
echo ========================================
pause
exit /b 0

:: ================================
:: Function: Build Linux with Docker
:: ================================
:BuildLinuxWithDocker
echo.
echo Building Linux binaries using Docker...
echo Creating Dockerfile...

:: Create temporary Dockerfile
set DOCKERFILE=%TEMP%\Dockerfile.pyinstaller
(
echo FROM python:3.10-slim
echo.
echo WORKDIR /app
echo.
echo RUN pip install --no-cache-dir pyinstaller
echo.
echo COPY requirements.txt* ./
echo RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
echo.
echo CMD ["/bin/bash"]
) > "%DOCKERFILE%"

:: Build backEnd for Linux
echo Building backEnd for Linux...
docker run --rm -v "%CD%\backEnd:/app" -w /app python:3.10-slim bash -c "pip install pyinstaller && pyinstaller --onefile --clean --noconfirm backEnd.py --distpath /app/dist_linux"
if exist "backEnd\dist_linux\backEnd" (
    move "backEnd\dist_linux\backEnd" "%LINUX_DIR%\backEnd"
    rmdir /s /q "backEnd\dist_linux"
)

:: Build Spider for Linux
echo Building Spider for Linux...
docker run --rm -v "%CD%\Spider:/app" -w /app python:3.10-slim bash -c "pip install pyinstaller && pyinstaller --onefile --clean --noconfirm Spider.py --distpath /app/dist_linux"
if exist "Spider\dist_linux\Spider" (
    move "Spider\dist_linux\Spider" "%LINUX_DIR%\Spider"
    rmdir /s /q "Spider\dist_linux"
)

:: Build WebServer for Linux
echo Building WebServer for Linux...
docker run --rm -v "%CD%\WebServer:/app" -w /app python:3.10-slim bash -c "pip install pyinstaller && pyinstaller --onefile --clean --noconfirm WebServer.py --distpath /app/dist_linux"
if exist "WebServer\dist_linux\WebServer" (
    move "WebServer\dist_linux\WebServer" "%LINUX_DIR%\WebServer"
    rmdir /s /q "WebServer\dist_linux"
)

:: Copy additional files for Linux
if exist "Releases\start_all.sh" (
    copy "Releases\start_all.sh" "%LINUX_DIR%\start_all.sh"
)
if exist "Releases\conf.ini" (
    copy "Releases\conf.ini" "%LINUX_DIR%\conf.ini"
)
if exist "Documents" (
    xcopy "Documents" "%LINUX_DIR%\Documents\" /E /I /H /Y /Q
)
if not exist "%LINUX_DIR%\log" mkdir "%LINUX_DIR%\log"

echo Linux build with Docker completed!
goto :eof

:: ================================
:: Function: Build Linux with WSL
:: ================================
:BuildLinuxWithWSL
echo.
echo Building Linux binaries using WSL2...

:: Convert Windows path to WSL path
for /f "delims=" %%i in ('wsl wslpath -a "%CD%"') do set WSL_PATH=%%i

:: Build backEnd for Linux
echo Building backEnd for Linux...
wsl bash -c "cd '%WSL_PATH%/backEnd' && python3 -m pip install pyinstaller && pyinstaller --onefile --clean --noconfirm backEnd.py --distpath ./dist_linux"
if exist "backEnd\dist_linux\backEnd" (
    if not exist "%LINUX_DIR%" mkdir "%LINUX_DIR%"
    move "backEnd\dist_linux\backEnd" "%LINUX_DIR%\backEnd"
    rmdir /s /q "backEnd\dist_linux"
)

:: Build Spider for Linux
echo Building Spider for Linux...
wsl bash -c "cd '%WSL_PATH%/Spider' && python3 -m pip install pyinstaller && pyinstaller --onefile --clean --noconfirm Spider.py --distpath ./dist_linux"
if exist "Spider\dist_linux\Spider" (
    move "Spider\dist_linux\Spider" "%LINUX_DIR%\Spider"
    rmdir /s /q "Spider\dist_linux"
)

:: Build WebServer for Linux
echo Building WebServer for Linux...
wsl bash -c "cd '%WSL_PATH%/WebServer' && python3 -m pip install pyinstaller && pyinstaller --onefile --clean --noconfirm WebServer.py --distpath ./dist_linux"
if exist "WebServer\dist_linux\WebServer" (
    move "WebServer\dist_linux\WebServer" "%LINUX_DIR%\WebServer"
    rmdir /s /q "WebServer\dist_linux"
)

:: Copy additional files for Linux
if exist "Releases\start_all.sh" (
    copy "Releases\start_all.sh" "%LINUX_DIR%\start_all.sh"
)
if exist "Releases\conf.ini" (
    copy "Releases\conf.ini" "%LINUX_DIR%\conf.ini"
)
if exist "Documents" (
    xcopy "Documents" "%LINUX_DIR%\Documents\" /E /I /H /Y /Q
)
if not exist "%LINUX_DIR%\log" mkdir "%LINUX_DIR%\log"

echo Linux build with WSL completed!
goto :eof