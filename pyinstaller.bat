@echo off
echo Starting PyInstaller packaging process...

:: Set version number (modify this for each release)
set VERSION=v2.3.4.4

:: Sync version to package.json
echo Syncing version to package.json...
:: Extract version number (remove 'v' prefix if present)
set VERSION_NUM=%VERSION%
if "%VERSION_NUM:~0,1%"=="v" set VERSION_NUM=%VERSION_NUM:~1%
:: Update package.json using PowerShell (via temp script)
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

:: Create Releases directory and version subdirectory if they don't exist
if not exist "Releases" mkdir Releases
if not exist "Releases\%VERSION%" mkdir "Releases\%VERSION%"
echo Creating release in: Releases\%VERSION%

:: Clear previous builds
echo Cleaning previous builds...
if exist "backEnd\dist" rmdir /s /q "backEnd\dist"
if exist "backEnd\build" rmdir /s /q "backEnd\build"
if exist "Spider\dist" rmdir /s /q "Spider\dist"
if exist "Spider\build" rmdir /s /q "Spider\build"
if exist "WebServer\dist" rmdir /s /q "WebServer\dist"
if exist "WebServer\build" rmdir /s /q "WebServer\build"

:: Package backEnd.py
echo.
echo [1/3] Packaging backEnd.exe...
cd backEnd
pyinstaller --onefile --clean --noconfirm backEnd.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package backEnd.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package Spider.py
echo.
echo [2/3] Packaging Spider.exe...
cd Spider
pyinstaller --onefile --clean --noconfirm Spider.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package Spider.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package WebServer.py
echo.
echo [3/3] Packaging WebServer.exe...
cd WebServer
pyinstaller --onefile --clean --noconfirm WebServer.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package WebServer.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Copy additional files to version folder
echo.
echo Copying additional files to version folder...
if exist "Releases\start_all.bat" (
    copy "Releases\start_all.bat" "Releases\%VERSION%\start_all.bat"
    echo start_all.bat copied successfully
) else (
    echo Warning: start_all.bat not found in Releases folder
)

if exist "Releases\conf.ini" (
    copy "Releases\conf.ini" "Releases\%VERSION%\conf.ini"
    echo conf.ini copied successfully
) else (
    echo Warning: conf.ini not found in Releases folder
)

:: Copy Documents folder
if exist "Documents" (
    echo Copying Documents folder...
    xcopy "Documents" "Releases\%VERSION%\Documents\" /E /I /H /Y /Q
    echo Documents folder copied successfully
) else (
    echo Warning: Documents folder not found
)

:: Build and copy WebSite
if exist "WebSite" (
    echo Building WebSite...
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
    
    :: Copy built dist folder
    if exist "WebSite\dist" (
        echo Copying WebSite dist folder...
        if not exist "Releases\%VERSION%\WebSite" mkdir "Releases\%VERSION%\WebSite"
        xcopy "WebSite\dist" "Releases\%VERSION%\WebSite\dist\" /E /I /H /Y /Q
        echo - WebSite dist folder copied successfully
    ) else (
        echo Error: WebSite dist folder not found after build
        pause
        exit /b 1
    )
) else (
    echo Warning: WebSite folder not found
)

:: Create log directory (required by both backEnd.exe and Spider.exe)
if not exist "Releases\%VERSION%\log" mkdir "Releases\%VERSION%\log"
echo log directory created successfully

:: Copy existing logs if they exist
if exist "logs" (
    xcopy "logs" "Releases\%VERSION%\logs" /E /I /H /Y
    echo logs folder copied successfully
) else (
    echo Warning: logs folder not found in root directory
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
echo All executables have been created in: Releases\%VERSION%
dir /b "Releases\%VERSION%\*.exe"
echo ========================================

:: Create ZIP file
echo.
echo Creating ZIP archive...

:: set ZIP_FILE=Releases\%VERSION%.zip
set ZIP_FILE=Releases\CsWeaponManager.zip
:: Remove old zip if exists
if exist "%ZIP_FILE%" (
    echo Removing old ZIP file...
    del /q "%ZIP_FILE%"
)

:: Use PowerShell to create ZIP archive with NoProfile to avoid path issues
echo Compressing files to %ZIP_FILE%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'Releases\%VERSION%\*' -DestinationPath '%ZIP_FILE%' -CompressionLevel Optimal -Force"

if %errorlevel% neq 0 (
    echo Warning: Failed to create ZIP archive
) else (
    echo.
    echo ========================================
    echo ZIP archive created successfully!
    echo ========================================
    echo Location: %ZIP_FILE%
    for %%A in ("%ZIP_FILE%") do echo Size: %%~zA bytes
    echo ========================================
)

pause