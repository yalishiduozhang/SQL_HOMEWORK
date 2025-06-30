@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ======================================
echo MovieHunter 一键启动脚本 (Windows)
echo ======================================
echo.

:: 设置控制台窗口标题
title MovieHunter 启动器

:: 检查Python是否安装
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+并添加到系统PATH
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✓ Python环境正常

:: 检查pip是否可用
echo.
echo [2/6] 检查pip包管理器...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ pip未安装或不可用
    echo 请重新安装Python并确保包含pip
    pause
    exit /b 1
)
echo ✓ pip包管理器正常

:: 检查MySQL是否安装和运行
echo.
echo [3/6] 检查MySQL服务...
sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ MySQL服务未找到
    echo 请确保MySQL已安装并启动服务
    echo 如果使用XAMPP/WAMP等集成环境，请先启动MySQL
    set /p continue="是否继续？MySQL可能在其他位置运行 (y/N): "
    if /i not "!continue!"=="y" (
        pause
        exit /b 1
    )
) else (
    sc query mysql | find "RUNNING" >nul
    if %errorlevel% neq 0 (
        echo ⚠ MySQL服务未运行，尝试启动...
        net start mysql >nul 2>&1
        if %errorlevel% neq 0 (
            echo ✗ 无法启动MySQL服务，请手动启动
            echo 或使用管理员权限运行此脚本
            pause
            exit /b 1
        )
        echo ✓ MySQL服务已启动
    ) else (
        echo ✓ MySQL服务正在运行
    )
)

:: 安装Python依赖
echo.
echo [4/6] 安装Python依赖包...
if not exist "requirements.txt" (
    echo ✗ requirements.txt文件不存在
    pause
    exit /b 1
)

echo 正在检查和安装Python依赖包...
echo 这可能需要几分钟时间，请耐心等待...

:: 配置pip镜像源加速下载
echo 配置pip镜像源以加速下载...
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

:: 首先升级pip使用镜像源
echo 1. 升级pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% neq 0 (
    echo ⚠ 使用清华镜像升级pip失败，尝试阿里镜像...
    python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if %errorlevel% neq 0 (
        echo ⚠ 使用阿里镜像升级pip失败，尝试官方源...
        python -m pip install --upgrade pip
    )
) else (
    echo ✓ pip升级成功（使用清华镜像）
)

:: 安装依赖包，优先使用清华镜像
echo 2. 安装Python依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% neq 0 (
    echo.
    echo ⚠ 清华镜像安装失败，尝试阿里云镜像...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if %errorlevel% neq 0 (
        echo ⚠ 阿里云镜像安装失败，尝试豆瓣镜像...
        pip install -r requirements.txt -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com
        if %errorlevel% neq 0 (
            echo ⚠ 豆瓣镜像安装失败，尝试官方源...
            pip install -r requirements.txt
            if %errorlevel% neq 0 (
                echo.
                echo ✗ 所有镜像源安装均失败
                echo 可能的解决方案：
                echo 1. 检查网络连接是否正常
                echo 2. 检查防火墙设置
                echo 3. 手动安装核心包：
                echo    pip install flask numpy pandas mysql-connector-python pillow
                echo.
                set /p continue="是否继续启动应用？部分功能可能不可用 (y/N): "
                if /i not "!continue!"=="y" (
                    pause
                    exit /b 1
                )
            ) else (
                echo ✓ Python依赖包安装完成（使用官方源）
            )
        ) else (
            echo ✓ Python依赖包安装完成（使用豆瓣镜像）
        )
    ) else (
        echo ✓ Python依赖包安装完成（使用阿里云镜像）
    )
) else (
    echo ✓ Python依赖包安装完成（使用清华镜像）
)

:: 检查数据文件
echo.
echo [5/6] 检查数据文件...
if not exist "data\movies.csv" (
    echo ⚠ data\movies.csv 文件不存在
    echo 应用可能无法正常显示电影数据
)
if not exist "data\ratings.csv" (
    echo ⚠ data\ratings.csv 文件不存在
    echo 应用可能无法正常显示评分数据
)
if not exist "schema.sql" (
    echo ✗ schema.sql 文件不存在
    echo 无法初始化数据库结构
    pause
    exit /b 1
)
echo ✓ 数据文件检查完成

:: 数据库初始化
echo.
echo [6/6] 初始化数据库...
echo 注意：首次运行需要输入MySQL数据库密码
echo.

if not exist "init_db.py" (
    echo ✗ init_db.py 文件不存在
    echo 无法初始化数据库
    pause
    exit /b 1
)

:: 询问是否需要初始化数据库
set /p init_db="是否需要初始化数据库？(首次运行请选择y) (y/N): "
if /i "!init_db!"=="y" (
    echo 正在初始化数据库...
    python init_db.py
    if %errorlevel% neq 0 (
        echo ✗ 数据库初始化失败
        echo 请检查MySQL连接和权限设置
        pause
        exit /b 1
    )
    echo ✓ 数据库初始化完成
) else (
    echo ✓ 跳过数据库初始化
)

:: 启动应用
echo.
echo ======================================
echo 启动MovieHunter应用...
echo ======================================
echo.
echo 应用启动后将在以下地址可访问：
echo 本地访问: http://localhost:6010
echo 局域网访问: http://您的IP地址:6010
echo.
echo 可用测试账号：
echo 用户名: test    密码: 123456
echo.
echo 按 Ctrl+C 可停止应用
echo ======================================
echo.

:: 启动Flask应用
python app.py

echo.
echo 应用已停止运行
pause
