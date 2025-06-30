@echo off
setlocal enabledelayedexpansion

title MovieHunter Fixed Build Tool

echo.
echo ===============================================================================
echo                          MovieHunter Fixed Build Tool
echo ===============================================================================
echo.
echo This will rebuild the EXE with proper file inclusion
echo.

set /p confirm="Continue with rebuilding? (y/N): "
if /i not "!confirm!"=="y" (
    echo Build cancelled
    pause
    exit /b 0
)

:: Clean old build files
echo.
echo [1/4] Cleaning old build files...
if exist "dist" (
    echo Removing old dist directory...
    rmdir /s /q "dist" >nul 2>&1
)
if exist "build" (
    echo Removing old build directory...
    rmdir /s /q "build" >nul 2>&1
)
echo SUCCESS: Environment cleaned

:: Check required files
echo.
echo [2/4] Checking required files...
set "missing_files="
if not exist "launcher.py" set "missing_files=!missing_files! launcher.py"
if not exist "app.py" set "missing_files=!missing_files! app.py"
if not exist "init_db.py" set "missing_files=!missing_files! init_db.py"
if not exist "templates" set "missing_files=!missing_files! templates/"
if not exist "static" set "missing_files=!missing_files! static/"
if not exist "data" set "missing_files=!missing_files! data/"

if defined missing_files (
    echo ERROR: Missing required files: !missing_files!
    pause
    exit /b 1
)
echo SUCCESS: All required files found

:: Execute packaging with explicit file inclusion
echo.
echo [3/4] Starting packaging with fixed parameters...
echo This may take several minutes, please wait...
echo.

pyinstaller ^
    --onedir ^
    --console ^
    --name "MovieHunter" ^
    --add-data "app.py;." ^
    --add-data "launcher.py;." ^
    --add-data "init_db.py;." ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "data;data" ^
    --add-data "schema.sql;." ^
    --add-data "requirements.txt;." ^
    --hidden-import "mysql.connector" ^
    --hidden-import "mysql.connector.pooling" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "flask" ^
    --hidden-import "numpy" ^
    --hidden-import "pandas" ^
    --hidden-import "hashlib" ^
    --hidden-import "secrets" ^
    --hidden-import "datetime" ^
    --hidden-import "decimal" ^
    --hidden-import "math" ^
    --hidden-import "collections" ^
    --hidden-import "getpass" ^
    --hidden-import "os" ^
    --noconfirm ^
    launcher.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Packaging failed
    pause
    exit /b 1
)

:: Post-processing
echo.
echo [4/4] Post-processing...
if exist "dist\MovieHunter" (
    echo Copying additional files...
    
    :: Ensure app.py is in the root directory for easy access
    if exist "app.py" copy "app.py" "dist\MovieHunter\" >nul 2>&1
    if exist "launcher.py" copy "launcher.py" "dist\MovieHunter\" >nul 2>&1
    if exist "init_db.py" copy "init_db.py" "dist\MovieHunter\" >nul 2>&1
    if exist "*.md" copy "*.md" "dist\MovieHunter\" >nul 2>&1
    
    :: Create improved startup script
    (
    echo @echo off
    echo title MovieHunter
    echo echo.
    echo echo ======================================
    echo echo MovieHunter Movie Recommendation System
    echo echo ======================================
    echo echo.
    echo echo Starting application, please wait...
    echo echo Current directory: %%CD%%
    echo echo.
    echo cd /d "%%~dp0"
    echo echo Changed to: %%CD%%
    echo echo.
    echo echo Checking files...
    echo if not exist "MovieHunter.exe" ^(
    echo     echo ERROR: MovieHunter.exe not found!
    echo     pause
    echo     exit /b 1
    echo ^)
    echo echo Files OK. Starting MovieHunter...
    echo echo.
    echo "MovieHunter.exe"
    echo echo.
    echo echo Application stopped.
    echo pause
    ) > "dist\MovieHunter\Start_MovieHunter.bat"
    
    :: Create debug script
    (
    echo @echo off
    echo title MovieHunter Debug
    echo echo Starting MovieHunter in debug mode...
    echo cd /d "%%~dp0"
    echo echo Current directory: %%CD%%
    echo echo.
    echo echo Listing files:
    echo dir /b
    echo echo.
    echo echo Starting application...
    echo "MovieHunter.exe"
    echo echo.
    echo echo Debug session ended.
    echo pause
    ) > "dist\MovieHunter\Debug_MovieHunter.bat"
    
    echo SUCCESS: Post-processing completed
) else (
    echo ERROR: Build directory not found
    pause
    exit /b 1
)

echo.
echo ======================================================================================================
echo Fixed build completed!
echo ======================================================================================================
echo.
echo Location: dist\MovieHunter\
echo Main program: MovieHunter.exe
echo Start script: Start_MovieHunter.bat
echo Debug script: Debug_MovieHunter.bat
echo.
echo To test:
echo 1. Go to dist\MovieHunter\ folder
echo 2. Double-click Start_MovieHunter.bat
echo 3. If issues persist, try Debug_MovieHunter.bat
echo.
echo ======================================================================================================

echo.
pause
