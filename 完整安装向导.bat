@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title MovieHunter 完整安装向导

:: 设置颜色（如果支持）
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                    MovieHunter 完整安装向导                                  %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m
echo.
echo %ESC%[93m此向导将帮助您：%ESC%[0m
echo %ESC%[93m1. 检查并安装所有必要的软件%ESC%[0m
echo %ESC%[93m2. 配置开发环境%ESC%[0m
echo %ESC%[93m3. 安装Python依赖包%ESC%[0m
echo %ESC%[93m4. 初始化数据库%ESC%[0m
echo %ESC%[93m5. 运行应用程序%ESC%[0m
echo %ESC%[93m6. 可选：打包为EXE文件%ESC%[0m
echo.
echo %ESC%[91m注意：安装过程中可能需要下载软件，请确保网络连接正常%ESC%[0m
echo.

set /p continue="是否继续安装向导？(y/N): "
if /i not "!continue!"=="y" (
    echo 安装向导已取消
    pause
    exit /b 0
)

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                              第1步：检查Python                               %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%[91m✗ Python未安装%ESC%[0m
    echo.
    echo %ESC%[93m正在为您打开Python官方下载页面...%ESC%[0m
    echo %ESC%[93m请下载Python 3.7+版本，安装时务必勾选 "Add Python to PATH"%ESC%[0m
    start https://www.python.org/downloads/windows/
    echo.
    echo %ESC%[93m安装Python后请重新运行此向导%ESC%[0m
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
    echo %ESC%[92m✓ Python已安装：!python_version!%ESC%[0m
)

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                              第2步：检查MySQL                                %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

sc query mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo %ESC%[91m✗ MySQL未安装%ESC%[0m
    echo.
    echo %ESC%[93m请选择MySQL安装方式：%ESC%[0m
    echo %ESC%[93m1. XAMPP（推荐，包含MySQL+Apache+PHP）%ESC%[0m
    echo %ESC%[93m2. MySQL Community Server（仅MySQL）%ESC%[0m
    echo %ESC%[93m3. MySQL Workbench + Server（图形界面）%ESC%[0m
    echo.
    set /p mysql_choice="请选择 (1-3): "
    
    if "!mysql_choice!"=="1" (
        echo %ESC%[93m正在打开XAMPP下载页面...%ESC%[0m
        start https://www.apachefriends.org/download.html
        echo %ESC%[93m请下载并安装XAMPP，然后启动MySQL服务%ESC%[0m
    ) else if "!mysql_choice!"=="2" (
        echo %ESC%[93m正在打开MySQL下载页面...%ESC%[0m
        start https://dev.mysql.com/downloads/mysql/
        echo %ESC%[93m请下载并安装MySQL Server%ESC%[0m
    ) else if "!mysql_choice!"=="3" (
        echo %ESC%[93m正在打开MySQL Workbench下载页面...%ESC%[0m
        start https://dev.mysql.com/downloads/workbench/
        echo %ESC%[93m请下载并安装MySQL Workbench（会自动安装Server）%ESC%[0m
    )
    
    echo.
    echo %ESC%[93m安装MySQL后请重新运行此向导%ESC%[0m
    pause
    exit /b 1
) else (
    echo %ESC%[92m✓ MySQL已安装%ESC%[0m
    sc query mysql | find "RUNNING" >nul
    if %errorlevel% neq 0 (
        echo %ESC%[93m⚠ MySQL服务未运行，尝试启动...%ESC%[0m
        net start mysql >nul 2>&1
        if %errorlevel% neq 0 (
            echo %ESC%[91m✗ 无法启动MySQL服务%ESC%[0m
            echo %ESC%[93m请手动启动MySQL服务或使用管理员权限运行此脚本%ESC%[0m
        ) else (
            echo %ESC%[92m✓ MySQL服务已启动%ESC%[0m
        )
    ) else (
        echo %ESC%[92m✓ MySQL服务正在运行%ESC%[0m
    )
)

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                           第3步：配置pip镜像源                               %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip" >nul 2>&1

echo %ESC%[93m配置pip使用国内镜像源以加速下载...%ESC%[0m
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

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                           第4步：安装Python依赖                              %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

echo %ESC%[93m正在升级pip...%ESC%[0m
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn >nul 2>&1

echo %ESC%[93m正在安装项目依赖包...%ESC%[0m
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
if %errorlevel% neq 0 (
    echo %ESC%[93m⚠ 清华镜像安装失败，尝试阿里云镜像...%ESC%[0m
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    if %errorlevel% neq 0 (
        echo %ESC%[91m✗ 依赖包安装失败%ESC%[0m
        pause
        exit /b 1
    )
)
echo %ESC%[92m✓ Python依赖包安装完成%ESC%[0m

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                             第5步：初始化数据库                              %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

echo %ESC%[93m准备初始化数据库...%ESC%[0m
echo %ESC%[93m注意：初始化过程中需要输入MySQL数据库密码%ESC%[0m
echo %ESC%[93m如果使用XAMPP，默认密码为空（直接按回车）%ESC%[0m
echo.

set /p init_choice="是否现在初始化数据库？(y/N): "
if /i "!init_choice!"=="y" (
    python init_db.py
    if %errorlevel% equ 0 (
        echo %ESC%[92m✓ 数据库初始化完成%ESC%[0m
    ) else (
        echo %ESC%[93m⚠ 数据库初始化可能失败，但可以稍后重试%ESC%[0m
    )
) else (
    echo %ESC%[93m✓ 跳过数据库初始化（可稍后手动执行）%ESC%[0m
)

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                             第6步：启动应用程序                              %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

echo %ESC%[93m是否现在启动MovieHunter？%ESC%[0m
set /p start_choice="(y/N): "
if /i "!start_choice!"=="y" (
    echo.
    echo %ESC%[92m🎉 正在启动MovieHunter...%ESC%[0m
    echo %ESC%[96m访问地址：http://localhost:6010%ESC%[0m
    echo %ESC%[96m测试账号：test / 123456%ESC%[0m
    echo.
    python app.py
)

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[96m                          第7步：可选 - EXE打包                               %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m

echo %ESC%[93m您可以将MovieHunter打包为独立的EXE文件，便于分发给其他用户%ESC%[0m
set /p pack_choice="是否现在打包为EXE文件？(y/N): "
if /i "!pack_choice!"=="y" (
    if exist "打包exe.bat" (
        call "打包exe.bat"
    ) else (
        echo %ESC%[91m✗ 打包脚本不存在%ESC%[0m
    )
)

echo.
echo %ESC%[96m===============================================================================%ESC%[0m
echo %ESC%[92m                            🎉 安装向导完成！                                 %ESC%[0m
echo %ESC%[96m===============================================================================%ESC%[0m
echo.
echo %ESC%[92m恭喜！MovieHunter已成功配置完成%ESC%[0m
echo.
echo %ESC%[96m📝 后续使用方法：%ESC%[0m
echo %ESC%[93m   - 双击"MovieHunter启动器.bat"选择功能%ESC%[0m
echo %ESC%[93m   - 或直接双击"quick_start.bat"快速启动%ESC%[0m
echo %ESC%[93m   - 或运行命令：python app.py%ESC%[0m
echo.
echo %ESC%[96m🌐 访问地址：http://localhost:6010%ESC%[0m
echo %ESC%[96m👤 测试账号：test / 123456%ESC%[0m
echo.
echo %ESC%[96m📚 更多帮助：查看 Windows启动指南.md%ESC%[0m
echo.
pause
