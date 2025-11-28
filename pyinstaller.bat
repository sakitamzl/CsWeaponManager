@echo off
echo Starting PyInstaller packaging process...

:: Set version number (modify this for each release)
set VERSION=v1.2.6

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

:: Package backEnd.py
echo.
echo [1/2] Packaging backEnd.exe...
cd backEnd
pyinstaller -F backEnd.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package backEnd.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package Spider.py
echo.
echo [2/2] Packaging Spider.exe...
cd Spider
pyinstaller -F Spider.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package Spider.py
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

if exist "WebSite" (
    echo Copying WebSite files and folders...
    
    :: Create WebSite directory
    if not exist "Releases\%VERSION%\WebSite" mkdir "Releases\%VERSION%\WebSite"
    
    :: Copy public folder (exclude weapon_imgs)
    if exist "WebSite\public" (
        xcopy "WebSite\public" "Releases\%VERSION%\WebSite\public\" /E /I /H /Y /Q
        if exist "Releases\%VERSION%\WebSite\public\weapon_imgs" (
            rmdir /s /q "Releases\%VERSION%\WebSite\public\weapon_imgs"
            echo - excluded weapon_imgs folder from public copy
        ) else (
            echo - public folder copied
        )
    )
    
    :: Copy src folder
    if exist "WebSite\src" (
        xcopy "WebSite\src" "Releases\%VERSION%\WebSite\src\" /E /I /H /Y /Q
        echo - src folder copied
    )
    
    :: Copy package.json
    if exist "WebSite\package.json" (
        copy "WebSite\package.json" "Releases\%VERSION%\WebSite\package.json" >nul
        echo - package.json copied
    )
    
    :: Copy package-lock.json
    if exist "WebSite\package-lock.json" (
        copy "WebSite\package-lock.json" "Releases\%VERSION%\WebSite\package-lock.json" >nul
        echo - package-lock.json copied
    )
    
    :: Copy vue.config.js
    if exist "WebSite\vue.config.js" (
        copy "WebSite\vue.config.js" "Releases\%VERSION%\WebSite\vue.config.js" >nul
        echo - vue.config.js copied
    )
    
    :: Copy README.md if exists
    if exist "WebSite\README.md" (
        copy "WebSite\README.md" "Releases\%VERSION%\WebSite\README.md" >nul
        echo - README.md copied
    )
    
    echo WebSite files copied successfully
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