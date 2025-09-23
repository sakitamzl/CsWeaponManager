@echo off
echo Starting PyInstaller packaging process...

:: Set version number (modify this for each release)
set VERSION=v1.0.1

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
echo [1/3] Packaging blankEndApi.exe...
cd blankEndApi
pyinstaller -F blankEndApi.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package blankEndApi.py
    cd ..
    pause
    exit /b 1
)
cd ..

:: Package getAppToken.py
echo.
echo [2/3] Packaging getAppToken.exe...
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
echo [3/3] Packaging Spider.exe...
cd Spider
pyinstaller -F Spider.py --distpath "..\Releases\%VERSION%"
if %errorlevel% neq 0 (
    echo Error: Failed to package Spider.py
    cd ..
    pause
    exit /b 1
)
cd ..

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
