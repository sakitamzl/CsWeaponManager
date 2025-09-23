@echo off
echo Starting PyInstaller packaging process...

:: Set version number (modify this for each release)
set VERSION=v1.0.2

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
if exist "blankEndApi\dist" rmdir /s /q "blankEndApi\dist"
if exist "blankEndApi\build" rmdir /s /q "blankEndApi\build"
if exist "getAppToken\dist" rmdir /s /q "getAppToken\dist"
if exist "getAppToken\build" rmdir /s /q "getAppToken\build"
if exist "Spider\dist" rmdir /s /q "Spider\dist"
if exist "Spider\build" rmdir /s /q "Spider\build"

:: Package blankEndApi.py
echo.
echo [1/4] Packaging blankEndApi.exe...
cd blankEndApi
pyinstaller -F blankEndApi.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package blankEndApi.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package setup_database.py
echo.
echo [2/4] Packaging setup_database.exe...
cd blankEndApi
pyinstaller -F setup_database.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package setup_database.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package getAppToken.py
echo.
echo [3/4] Packaging getAppToken.exe...
cd getAppToken
pyinstaller -F getAppToken.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package getAppToken.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package Spider.py
echo.
echo [4/4] Packaging Spider.exe...
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

if exist "blankEndApi\DB.sql" (
    copy "blankEndApi\DB.sql" "Releases\%VERSION%\DB.sql"
    echo DB.sql copied successfully
) else (
    echo Warning: DB.sql not found in blankEndApi folder
)

if exist "WebSite" (
    xcopy "WebSite" "Releases\%VERSION%\WebSite" /E /I /H /Y
    echo WebSite folder copied successfully
) else (
    echo Warning: WebSite folder not found in root directory
)

:: Create log directory (required by both blankEndApi.exe and Spider.exe)
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
if exist "blankEndApi\build" rmdir /s /q "blankEndApi\build"
if exist "blankEndApi\*.spec" del /q "blankEndApi\*.spec"
if exist "getAppToken\build" rmdir /s /q "getAppToken\build"
if exist "getAppToken\*.spec" del /q "getAppToken\*.spec"
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
pause