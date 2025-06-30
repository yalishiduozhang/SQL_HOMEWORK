@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title MovieHunter 一键启动器 - 完整版

:: 设置颜色代码
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

echo.
echo %ESC%[92m     ███╗   ███╗ ██████╗ ██╗   ██╗██╗███████╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ %ESC%[0m
echo %ESC%[92m     ████╗ ████║██╔═══██╗██║   ██║██║██╔════╝██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗%ESC%[0m
echo %ESC%[92m     ██╔████╔██║██║   ██║██║   ██║██║█████╗  ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝%ESC%[0m
echo %ESC%[92m     ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██║██╔══╝  ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗%ESC%[0m
echo %ESC%[92m     ██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ██║███████╗██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║%ESC%[0m
echo %ESC%[92m     ╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝%ESC%[0m
echo.
echo %ESC%[96m                                 Windows 一键初始化启动器%ESC%[0m
echo %ESC%[93m                              支持全自动环境配置和镜像源加速%ESC%[0m
echo.
echo %ESC%[95m======================================================================================================%ESC%[0m

echo.
echo %ESC%[93m正在执行一键初始化流程...%ESC%[0m
echo.

:: ========== 第1步：检查和安装Python ==========
echo %ESC%[96m[1/7] 检查Python环境...%ESC%[0m
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%[91m✗ Python未安装或未添加到PATH%ESC%[0m
    echo.
    echo %ESC%[93m自动打开Python官网下载页面...%ESC%[0m
    echo %ESC%[93m请下载Python 3.7+版本，安装时务必勾选 "Add Python to PATH"%ESC%[0m
    start https://www.python.org/downloads/
    echo.
    echo %ESC%[91m安装Python后请重新运行此脚本%ESC%[0m
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
    echo %ESC%[92m✓ Python环境正常：!python_version!%ESC%[0m
)

:: ========== 第2步：配置pip镜像源 ==========
echo.
echo %ESC%[96m[2/7] 配置pip镜像源...%ESC%[0m
if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip" >nul 2>&1

:: 创建pip配置文件
(
echo [global]
echo index-url = https://pypi.tuna.tsinghua.edu.cn/simple
echo trusted-host = pypi.tuna.tsinghua.edu.cn
echo timeout = 120
echo [install]
echo trusted-host = pypi.tuna.tsinghua.edu.cn
) > "%APPDATA%\pip\pip.ini"

if exist "%APPDATA%\pip\pip.ini" (
    echo %ESC%[92m✓ pip镜像源配置完成（清华大学镜像）%ESC%[0m
) else (
    echo %ESC%[93m⚠ pip配置文件创建失败，将在安装时手动指定镜像源%ESC%[0m
)

:: ========== 第3步：升级pip ==========
echo.
echo %ESC%[96m[3/7] 升级pip包管理器...%ESC%[0m
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%[93m⚠ 清华镜像升级失败，尝试阿里云镜像...%ESC%[0m
    python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com >nul 2>&1
    if %errorlevel% neq 0 (
        echo %ESC%[93m⚠ 阿里云镜像升级失败，使用官方源...%ESC%[0m
        python -m pip install --upgrade pip >nul 2>&1
    fi
fi
echo %ESC%[92m✓ pip升级完成%ESC%[0m

:: ========== 第4步：检查MySQL ==========
echo.
echo %ESC%[96m[4/7] 检查MySQL服务...%ESC%[0m
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%[93m⚠ MySQL服务未找到%ESC%[0m
    echo.
    echo %ESC%[93m自动打开XAMPP下载页面（推荐）...%ESC%[0m
    echo %ESC%[93mXAMPP包含MySQL、Apache等，安装简单%ESC%[0m
    start https://www.apachefriends.org/
    echo.
    echo %ESC%[91m请安装XAMPP并启动MySQL服务后重新运行此脚本%ESC%[0m
    echo %ESC%[93m或者您可以选择其他MySQL安装方式%ESC%[0m
    pause
    exit /b 1
) else (
    sc query mysql | find "RUNNING" >nul
    if %errorlevel% neq 0 (
        echo %ESC%[93m⚠ MySQL服务未运行，尝试启动...%ESC%[0m
        net start mysql >nul 2>&1
        if %errorlevel% neq 0 (
            echo %ESC%[91m✗ 无法启动MySQL服务%ESC%[0m
            echo %ESC%[93m请手动启动MySQL服务或使用管理员权限运行此脚本%ESC%[0m
            pause
            exit /b 1
        ) else (
            echo %ESC%[92m✓ MySQL服务已启动%ESC%[0m
        )
    ) else (
        echo %ESC%[92m✓ MySQL服务正在运行%ESC%[0m
    )
)

:: ========== 第5步：安装Python依赖 ==========
echo.
echo %ESC%[96m[5/7] 安装Python依赖包...%ESC%[0m
if not exist "requirements.txt" (
    echo %ESC%[91m✗ requirements.txt文件不存在%ESC%[0m
    pause
    exit /b 1
)

echo %ESC%[93m正在使用镜像源安装依赖包，请稍候...%ESC%[0m

:: 尝试多个镜像源
set "mirrors[0]=https://pypi.tuna.tsinghua.edu.cn/simple pypi.tuna.tsinghua.edu.cn 清华大学"
set "mirrors[1]=https://mirrors.aliyun.com/pypi/simple/ mirrors.aliyun.com 阿里云"
set "mirrors[2]=https://pypi.douban.com/simple/ pypi.douban.com 豆瓣"

for /L %%i in (0,1,2) do (
    for /f "tokens=1,2,3" %%a in ("!mirrors[%%i]!") do (
        echo 尝试使用%%c镜像源...
        pip install -r requirements.txt -i %%a --trusted-host %%b >nul 2>&1
        if !errorlevel! equ 0 (
            echo %ESC%[92m✓ 依赖包安装成功（使用%%c镜像）%ESC%[0m
            goto :deps_installed
        ) else (
            echo %ESC%[93m⚠ %%c镜像安装失败%ESC%[0m
        )
    )
)

:: 最后尝试官方源
echo 尝试使用官方源...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%[91m✗ 所有镜像源安装均失败%ESC%[0m
    echo.
    echo %ESC%[93m请手动执行以下命令之一：%ESC%[0m
    echo %ESC%[93mpip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple%ESC%[0m
    echo %ESC%[93mpip install flask numpy pandas mysql-connector-python pillow%ESC%[0m
    pause
    exit /b 1
) else (
    echo %ESC%[92m✓ 依赖包安装成功（使用官方源）%ESC%[0m
)

:deps_installed

:: ========== 第6步：检查数据文件 ==========
echo.
echo %ESC%[96m[6/7] 检查数据文件...%ESC%[0m
set "missing_files="
if not exist "data\movies.csv" set "missing_files=!missing_files! movies.csv"
if not exist "data\ratings.csv" set "missing_files=!missing_files! ratings.csv"
if not exist "schema.sql" set "missing_files=!missing_files! schema.sql"

if defined missing_files (
    echo %ESC%[93m⚠ 缺少数据文件：!missing_files!%ESC%[0m
    echo %ESC%[93m应用功能可能受限%ESC%[0m
) else (
    echo %ESC%[92m✓ 数据文件检查完成%ESC%[0m
)

:: ========== 第7步：数据库初始化 ==========
echo.
echo %ESC%[96m[7/7] 数据库初始化...%ESC%[0m
if not exist "init_db.py" (
    echo %ESC%[91m✗ init_db.py 文件不存在%ESC%[0m
    echo %ESC%[93m跳过数据库初始化%ESC%[0m
) else (
    echo %ESC%[93m注意：初始化过程中需要输入MySQL数据库密码%ESC%[0m
    echo %ESC%[93m如果是XAMPP环境，默认密码为空（直接按回车）%ESC%[0m
    echo.
    set /p init_db="是否初始化数据库？(首次运行建议选择 y) [y/N]: "
    if /i "!init_db!"=="y" (
        echo %ESC%[93m正在初始化数据库...%ESC%[0m
        python init_db.py
        if %errorlevel% neq 0 (
            echo %ESC%[91m✗ 数据库初始化失败%ESC%[0m
            echo %ESC%[93m请检查MySQL连接和权限设置%ESC%[0m
            set /p continue="是否继续启动应用？ [y/N]: "
            if /i not "!continue!"=="y" (
                pause
                exit /b 1
            )
        ) else (
            echo %ESC%[92m✓ 数据库初始化完成%ESC%[0m
        )
    ) else (
        echo %ESC%[93m✓ 跳过数据库初始化%ESC%[0m
    )
)

:: ========== 启动应用 ==========
echo.
echo %ESC%[95m======================================================================================================%ESC%[0m
echo %ESC%[92m                                    🎉 初始化完成！启动应用中... 🎉%ESC%[0m
echo %ESC%[95m======================================================================================================%ESC%[0m
echo.
echo %ESC%[96m应用启动后将在以下地址可访问：%ESC%[0m
echo %ESC%[93m🌐 本地访问：    http://localhost:6010%ESC%[0m
echo %ESC%[93m🌐 局域网访问：  http://您的IP地址:6010%ESC%[0m
echo.
echo %ESC%[96m可用测试账号：%ESC%[0m
echo %ESC%[93m👤 用户名: test      密码: 123456      （全新测试账号）%ESC%[0m
echo %ESC%[93m👤 用户名: user_1    密码: password    （包含历史数据）%ESC%[0m
echo.
echo %ESC%[91m按 Ctrl+C 可停止应用%ESC%[0m
echo %ESC%[95m======================================================================================================%ESC%[0m
echo.

:: 启动Flask应用
python app.py

echo.
echo %ESC%[93m应用已停止运行%ESC%[0m
echo %ESC%[96m感谢使用 MovieHunter！%ESC%[0m
pause
