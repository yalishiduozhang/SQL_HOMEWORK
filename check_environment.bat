@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ======================================
echo MovieHunter 环境检查和安装指南
echo ======================================
echo.

:: 检查Python
echo [1/3] 检查Python安装...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python未安装
    echo.
    echo 请按照以下步骤安装Python：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载最新版本的Python 3.7+
    echo 3. 安装时务必勾选 "Add Python to PATH"
    echo 4. 安装完成后重新运行此脚本
    echo.
    set /p open_browser="是否打开Python下载页面？ (y/N): "
    if /i "!open_browser!"=="y" (
        start https://www.python.org/downloads/
    )
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
    echo ✓ Python已安装：!python_version!
)

:: 检查pip
echo.
echo [2/3] 检查pip包管理器...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ pip不可用
    echo 请重新安装Python并确保包含pip
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%a in ('pip --version 2^>^&1') do set pip_version=%%a
    echo ✓ pip已安装：!pip_version!
    
    echo.
    echo 配置pip国内镜像源以加速下载...
    echo 正在创建pip配置文件...
    
    :: 创建pip配置目录
    if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip"
    
    :: 写入pip配置文件
    (
    echo [global]
    echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple
    echo trusted-host = pypi.tuna.tsinghua.edu.cn
    echo [install]
    echo trusted-host = pypi.tuna.tsinghua.edu.cn
    ) > "%APPDATA%\pip\pip.ini"
    
    if exist "%APPDATA%\pip\pip.ini" (
        echo ✓ pip镜像源配置完成（清华大学镜像）
        echo   配置文件位置：%APPDATA%\pip\pip.ini
    ) else (
        echo ⚠ pip镜像源配置失败，将在安装时手动指定
    )
)

:: 检查MySQL
echo.
echo [3/3] 检查MySQL安装...
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ MySQL服务未找到
    echo.
    echo 请选择以下MySQL安装方式之一：
    echo.
    echo 【推荐】方式1：安装XAMPP（包含MySQL、Apache等）
    echo 1. 访问 https://www.apachefriends.org/
    echo 2. 下载并安装XAMPP
    echo 3. 启动XAMPP控制面板
    echo 4. 启动MySQL服务
    echo.
    echo 方式2：单独安装MySQL
    echo 1. 访问 https://dev.mysql.com/downloads/mysql/
    echo 2. 下载MySQL Community Server
    echo 3. 安装并配置root密码
    echo 4. 确保MySQL服务已启动
    echo.
    echo 方式3：使用MySQL Workbench + MySQL Server
    echo 1. 访问 https://dev.mysql.com/downloads/workbench/
    echo 2. 下载并安装MySQL Workbench
    echo 3. 按提示安装MySQL Server
    echo.
    set /p choice="选择安装方式 (1-XAMPP/2-MySQL/3-Workbench/N-跳过): "
    if /i "!choice!"=="1" (
        start https://www.apachefriends.org/
    ) else if /i "!choice!"=="2" (
        start https://dev.mysql.com/downloads/mysql/
    ) else if /i "!choice!"=="3" (
        start https://dev.mysql.com/downloads/workbench/
    )
    echo.
    echo 安装完成后，请重新运行 start_windows.bat
    pause
    exit /b 1
) else (
    echo ✓ MySQL服务已安装
    sc query mysql | find "RUNNING" >nul
    if %errorlevel% neq 0 (
        echo ⚠ MySQL服务未运行
        echo 请手动启动MySQL服务或重启电脑
    ) else (
        echo ✓ MySQL服务正在运行
    )
)

echo.
echo ======================================
echo 环境检查完成！
echo ======================================
echo.
echo ✓ 所有必要软件都已安装
echo ✓ pip镜像源已配置（加速依赖包下载）
echo.
echo 现在可以运行以下步骤：
echo 1. 双击 MovieHunter启动器.bat
echo 2. 选择 "2. 完整初始化和启动"
echo 3. 或者直接运行 start_windows.bat
echo.
echo 常用镜像源地址（如需手动配置）：
echo - 清华大学：https://pypi.tuna.tsinghua.edu.cn/simple
echo - 阿里云：  https://mirrors.aliyun.com/pypi/simple/
echo - 豆瓣：    https://pypi.douban.com/simple/
echo.
pause
