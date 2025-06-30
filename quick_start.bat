@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title MovieHunter 快速启动

echo ======================================
echo MovieHunter 快速启动 (Windows)
echo ======================================
echo.

:: 快速检查Python和依赖
echo 检查环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python环境异常
    echo 请使用 start_windows.bat 进行完整初始化
    pause
    exit /b 1
)

:: 检查pip配置
if not exist "%APPDATA%\pip\pip.ini" (
    echo 配置pip镜像源以加速下载...
    if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip"
    (
    echo [global]
    echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple
    echo trusted-host = pypi.tuna.tsinghua.edu.cn
    echo [install]
    echo trusted-host = pypi.tuna.tsinghua.edu.cn
    ) > "%APPDATA%\pip\pip.ini"
    echo ✓ pip镜像源配置完成
)

:: 检查MySQL
echo 检查MySQL服务...
sc query mysql | find "RUNNING" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ MySQL服务未运行，尝试启动...
    net start mysql >nul 2>&1
    if %errorlevel% neq 0 (
        echo ✗ 无法启动MySQL，请手动启动或使用管理员权限
        pause
        exit /b 1
    )
)

:: 直接启动应用
echo.
echo ======================================
echo 启动MovieHunter应用...
echo ======================================
echo.
echo 访问地址: http://localhost:6010
echo 测试账号: test / 123456
echo.
echo 按 Ctrl+C 停止应用
echo ======================================
echo.

python app.py
