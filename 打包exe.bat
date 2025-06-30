@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title MovieHunter EXE打包工具

echo.
echo     ███╗   ███╗ ██████╗ ██╗   ██╗██╗███████╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
echo     ████╗ ████║██╔═══██╗██║   ██║██║██╔════╝██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
echo     ██╔████╔██║██║   ██║██║   ██║██║█████╗  ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
echo     ██║╚██╔╝██║██║   ██║╚██╗ ██╔╝██║██╔══╝  ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
echo     ██║ ╚═╝ ██║╚██████╔╝ ╚████╔╝ ██║███████╗██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
echo     ╚═╝     ╚═╝ ╚═════╝   ╚═══╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
echo.
echo                                    Windows EXE 打包工具
echo                                  将MovieHunter打包为独立可执行文件
echo.
echo ======================================================================================================

:: 设置镜像源
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

echo 📝 打包说明：
echo    本工具将把MovieHunter打包为Windows可执行文件（EXE）
echo    打包后的程序可以在没有Python环境的Windows机器上运行
echo    打包过程可能需要5-15分钟，请耐心等待
echo.

set /p confirm="是否继续打包？ (y/N): "
if /i not "!confirm!"=="y" (
    echo 打包已取消
    pause
    exit /b 0
)

:: 检查Python环境
echo.
echo [1/8] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python未安装或未添加到PATH
    echo 请先安装Python 3.7+并添加到PATH
    pause
    exit /b 1
)

for /f "tokens=2" %%a in ('python --version 2^>^&1') do set python_version=%%a
echo ✓ Python环境正常：!python_version!

:: 创建图标文件
echo.
echo [2/8] 创建应用图标...
if not exist "static\images\logo.ico" (
    echo 正在生成应用图标...
    python create_icon.py
    if !errorlevel! neq 0 (
        echo ⚠ 图标生成失败，将使用默认图标
    )
) else (
    echo ✓ 图标文件已存在
)

:: 检查并安装PyInstaller
echo.
echo [3/8] 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ PyInstaller未安装，正在安装...
    pip install pyinstaller -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
    if %errorlevel% neq 0 (
        echo ✗ PyInstaller安装失败，尝试其他镜像源...
        pip install pyinstaller -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
        if %errorlevel% neq 0 (
            echo ✗ PyInstaller安装失败
            pause
            exit /b 1
        )
    )
    echo ✓ PyInstaller安装成功
) else (
    echo ✓ PyInstaller已安装
)

:: 检查必要文件
echo.
echo [4/8] 检查项目文件...
set "missing_files="
if not exist "app.py" set "missing_files=!missing_files! app.py"
if not exist "requirements.txt" set "missing_files=!missing_files! requirements.txt"
if not exist "templates" set "missing_files=!missing_files! templates/"
if not exist "static" set "missing_files=!missing_files! static/"

if defined missing_files (
    echo ✗ 缺少必要文件：!missing_files!
    pause
    exit /b 1
)
echo ✓ 项目文件检查完成

:: 安装依赖
echo.
echo [5/8] 安装项目依赖...
echo 正在安装Python依赖包...
pip install -r requirements.txt -i %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST% >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ 清华镜像安装失败，尝试阿里云镜像...
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com >nul 2>&1
    if %errorlevel% neq 0 (
        echo ✗ 依赖安装失败
        pause
        exit /b 1
    )
)
echo ✓ 依赖安装完成

:: 清理旧的打包文件
echo.
echo [6/8] 清理打包环境...
if exist "dist" (
    echo 删除旧的dist目录...
    rmdir /s /q "dist" >nul 2>&1
)
if exist "build" (
    echo 删除旧的build目录...
    rmdir /s /q "build" >nul 2>&1
)
if exist "*.spec" (
    echo 发现现有spec文件...
)
echo ✓ 环境清理完成

:: 执行打包
echo.
echo [7/8] 开始打包...
echo 正在打包MovieHunter，这可能需要几分钟时间...
echo 请耐心等待，不要关闭窗口...
echo.

:: 使用spec文件打包
if exist "moviehunter.spec" (
    echo 使用自定义spec文件打包...
    pyinstaller moviehunter.spec --clean --noconfirm
) else (
    echo 使用命令行参数打包...
    pyinstaller ^
        --onedir ^
        --console ^
        --name "MovieHunter" ^
        --icon "static/images/logo.ico" ^
        --add-data "templates;templates" ^
        --add-data "static;static" ^
        --add-data "data;data" ^
        --add-data "schema.sql;." ^
        --add-data "requirements.txt;." ^
        --hidden-import "mysql.connector" ^
        --hidden-import "mysql.connector.pooling" ^
        --hidden-import "PIL" ^
        --hidden-import "PIL.Image" ^
        --collect-all "mysql.connector" ^
        --collect-all "PIL" ^
        --noconfirm ^
        app.py
)

if %errorlevel% neq 0 (
    echo.
    echo ✗ 打包失败
    echo 可能的原因：
    echo 1. 依赖包版本冲突
    echo 2. 磁盘空间不足
    echo 3. 杀毒软件阻止
    echo.
    echo 建议解决方案：
    echo 1. 检查是否有足够的磁盘空间（建议至少2GB）
    echo 2. 临时关闭杀毒软件
    echo 3. 以管理员权限运行
    pause
    exit /b 1
)

:: 后处理和文件复制
echo.
echo [8/8] 后处理和优化...
if exist "dist\MovieHunter" (
    echo 复制配置文件和脚本...
    
    :: 复制重要文件
    if exist "init_db.py" copy "init_db.py" "dist\MovieHunter\" >nul 2>&1
    if exist "*.md" copy "*.md" "dist\MovieHunter\" >nul 2>&1
    
    :: 创建用户友好的启动脚本
    (
    echo @echo off
    echo chcp 65001 ^>nul
    echo title MovieHunter
    echo echo.
    echo echo ======================================
    echo echo MovieHunter 电影推荐系统
    echo echo ======================================
    echo echo.
    echo echo 正在启动应用，请稍候...
    echo echo.
    echo cd /d "%%~dp0"
    echo start "" "MovieHunter.exe"
    echo echo.
    echo echo 🎬 MovieHunter已启动！
    echo echo.
    echo echo 📱 请在浏览器中访问：
    echo echo    http://localhost:6010
    echo echo.
    echo echo 👤 测试账号：
    echo echo    用户名: test
    echo echo    密码:   123456
    echo echo.
    echo echo 💡 注意：
    echo echo    1. 请确保MySQL服务已启动
    echo echo    2. 首次运行需要初始化数据库
    echo echo    3. 按Ctrl+C可停止程序
    echo echo.
    echo echo ======================================
    echo pause
    ) > "dist\MovieHunter\🚀启动MovieHunter.bat"
    
    :: 创建数据库初始化脚本
    (
    echo @echo off
    echo chcp 65001 ^>nul
    echo title 数据库初始化
    echo echo.
    echo echo ======================================
    echo echo MovieHunter 数据库初始化
    echo echo ======================================
    echo echo.
    echo echo 注意：请确保MySQL服务已启动
    echo echo.
    echo cd /d "%%~dp0"
    echo python init_db.py
    echo echo.
    echo echo 初始化完成！
    echo pause
    ) > "dist\MovieHunter\🔧初始化数据库.bat"
    
    :: 创建README文件
    (
    echo # MovieHunter 独立运行版
    echo.
    echo ## 快速开始
    echo.
    echo 1. 确保您的计算机已安装MySQL并启动服务
    echo 2. 双击"🚀启动MovieHunter.bat"
    echo 3. 在浏览器中访问 http://localhost:6010
    echo.
    echo ## 首次使用
    echo.
    echo 1. 双击"🔧初始化数据库.bat"初始化数据库
    echo 2. 按提示输入MySQL密码
    echo 3. 等待初始化完成
    echo 4. 双击"🚀启动MovieHunter.bat"启动应用
    echo.
    echo ## 测试账号
    echo.
    echo - 用户名: test
    echo - 密码: 123456
    echo.
    echo ## 注意事项
    echo.
    echo - 确保MySQL服务正在运行
    echo - 首次启动可能较慢，请耐心等待
    echo - 如有问题，请查看控制台错误信息
    echo.
    echo ## 系统要求
    echo.
    echo - Windows 7/8/10/11
    echo - MySQL 5.7+
    echo - 至少500MB磁盘空间
    ) > "dist\MovieHunter\README.txt"
    
    echo ✓ 文件复制和脚本创建完成
) else (
    echo ✗ 打包目录不存在，打包可能失败
    pause
    exit /b 1
)

:: 计算文件大小
echo.
echo 正在计算打包大小...
for /f %%i in ('powershell -command "Get-ChildItem -Path 'dist\MovieHunter' -Recurse | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum"') do set total_size=%%i
set /a size_mb=!total_size! / 1024 / 1024

echo.
echo ======================================================================================================
echo 🎉 打包完成！
echo ======================================================================================================
echo.
echo 📦 打包结果：
echo    位置：    dist\MovieHunter\
echo    大小：    约 !size_mb! MB
echo    主程序：  MovieHunter.exe
echo.
echo 📂 分发文件：
echo    🚀启动MovieHunter.bat  - 主启动脚本
echo    🔧初始化数据库.bat     - 数据库初始化工具
echo    README.txt             - 使用说明
echo    MovieHunter.exe        - 主程序
echo    其他依赖文件...
echo.
echo � 分发说明：
echo    1. 将整个 dist\MovieHunter 文件夹打包分发
echo    2. 用户需要安装MySQL并启动服务
echo    3. 双击"🚀启动MovieHunter.bat"即可运行
echo.
echo  重要提示：
echo    - EXE文件较大（!size_mb!MB）是正常的，包含了Python运行时
echo    - 首次启动可能需要30秒-1分钟，请耐心等待
echo    - 建议创建ZIP压缩包进行分发
echo    - 确保目标机器有足够的磁盘空间和内存
echo.
echo 🎯 下一步：
echo    可以将dist\MovieHunter文件夹压缩为ZIP文件进行分发
echo ======================================================================================================

:: 询问是否创建压缩包
echo.
set /p create_zip="是否创建ZIP压缩包便于分发？ (y/N): "
if /i "!create_zip!"=="y" (
    echo.
    echo 正在创建ZIP压缩包...
    powershell -command "Compress-Archive -Path 'dist\MovieHunter' -DestinationPath 'MovieHunter-Windows.zip' -Force"
    if !errorlevel! equ 0 (
        echo ✓ ZIP压缩包创建成功：MovieHunter-Windows.zip
    ) else (
        echo ⚠ ZIP压缩包创建失败，请手动压缩dist\MovieHunter文件夹
    )
)

echo.
pause
