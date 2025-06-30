@echo off
setlocal enabledelayedexpansion

title MovieHunter Build Tool

echo.
echo ===============================================================================
echo                          MovieHunter Build Tool
echo ===============================================================================
echo.
echo This tool will package MovieHunter as a Windows executable file
echo The packaging process may take 5-15 minutes, please be patient
echo.

set /p confirm="Continue with packaging? (y/N): "
if /i not "!confirm!"=="y" (
    echo Packaging cancelled
    pause
    exit /b 0
)

:: Check Python environment
echo.
echo [1/6] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed or not in PATH
    echo Please install Python 3.7+ and add to PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
echo SUCCESS: Python environment OK: !python_version!

:: Check and install PyInstaller
echo.
echo [2/6] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: PyInstaller not installed, installing...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: PyInstaller installation failed
        pause
        exit /b 1
    )
    echo SUCCESS: PyInstaller installed
) else (
    echo SUCCESS: PyInstaller already installed
)

:: Install dependencies
echo.
echo [3/6] Installing project dependencies...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Installation failed, trying with mirror...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Dependencies installation failed
        pause
        exit /b 1
    )
)
echo SUCCESS: Dependencies installed

:: Clean old build files
echo.
echo [4/6] Cleaning build environment...
if exist "dist" (
    echo Removing old dist directory...
    rmdir /s /q "dist" >nul 2>&1
)
if exist "build" (
    echo Removing old build directory...
    rmdir /s /q "build" >nul 2>&1
)
echo SUCCESS: Environment cleaned

:: Execute packaging
echo.
echo [5/6] Starting packaging...
echo Packaging MovieHunter, this may take several minutes...
echo Please wait, do not close the window...
echo.

:: Use simplified command line parameters for packaging
pyinstaller --onedir --console --name "MovieHunter" --add-data "templates;templates" --add-data "static;static" --add-data "data;data" --add-data "schema.sql;." --add-data "requirements.txt;." --add-data "init_db.py;." --hidden-import "mysql.connector" --hidden-import "PIL" --hidden-import "flask" --hidden-import "numpy" --hidden-import "pandas" --noconfirm launcher.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Packaging failed
    echo Possible causes:
    echo 1. Dependency package version conflicts
    echo 2. Insufficient disk space
    echo 3. Antivirus software blocking
    echo.
    echo Suggested solutions:
    echo 1. Check if there is enough disk space (recommend at least 2GB)
    echo 2. Temporarily disable antivirus software
    echo 3. Run with administrator privileges
    pause
    exit /b 1
)

:: Post-processing
echo.
echo [6/6] Post-processing and optimization...
if exist "dist\MovieHunter" (
    echo Copying configuration files and scripts...
    
    :: Copy important files
    if exist "init_db.py" copy "init_db.py" "dist\MovieHunter\" >nul 2>&1
    if exist "*.md" copy "*.md" "dist\MovieHunter\" >nul 2>&1
    
    :: Create startup script
    (
    echo @echo off
    echo title MovieHunter
    echo echo.
    echo echo ======================================
    echo echo MovieHunter Movie Recommendation System
    echo echo ======================================
    echo echo.
    echo echo Starting application, please wait...
    echo echo.
    echo cd /d "%%~dp0"
    echo start "" "MovieHunter.exe"
    echo echo.
    echo echo MovieHunter started!
    echo echo.
    echo echo Please visit in browser:
    echo echo    http://localhost:6010
    echo echo.
    echo echo Test account:
    echo echo    Username: test
    echo echo    Password: 123456
    echo echo.
    echo echo Notes:
    echo echo    1. Please ensure MySQL service is running
    echo echo    2. First run requires database initialization
    echo echo    3. Press Ctrl+C to stop the program
    echo echo.
    echo echo ======================================
    echo pause
    ) > "dist\MovieHunter\Start_MovieHunter.bat"
    
    echo SUCCESS: File copying and script creation completed
) else (
    echo ERROR: Package directory does not exist, packaging may have failed
    pause
    exit /b 1
)

echo.
echo ======================================================================================================
echo Packaging completed!
echo ======================================================================================================
echo.
echo Package results:
echo    Location:     dist\MovieHunter\
echo    Main program: MovieHunter.exe
echo    Start script: Start_MovieHunter.bat
echo.
echo Distribution instructions:
echo    1. Package and distribute the entire dist\MovieHunter folder
echo    2. Users need to install MySQL and start the service
echo    3. Double-click "Start_MovieHunter.bat" to run
echo.
echo Important notes:
echo    - Large EXE file size is normal, includes Python runtime
echo    - First startup may take 30 seconds to 1 minute, please be patient
echo    - Recommend creating ZIP archive for distribution
echo ======================================================================================================

echo.
pause
