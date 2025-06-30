@echo off
setlocal enabledelayedexpansion

title MovieHunter Minimal Build Tool

echo.
echo ===============================================================================
echo                    MovieHunter 精简版打包工具
echo              专门用于减小EXE文件体积的优化版本
echo ===============================================================================
echo.
echo 本工具将使用严格的排除策略来减小最终EXE文件的体积
echo 预计可以将体积从400MB+减少到100MB以内
echo.

set /p confirm="继续精简打包？(y/N): "
if /i not "!confirm!"=="y" (
    echo 打包取消
    pause
    exit /b 0
)

:: 清理旧的构建文件
echo.
echo [1/6] 清理旧的构建文件...
if exist "dist" (
    echo 删除旧的dist目录...
    rmdir /s /q "dist" >nul 2>&1
)
if exist "build" (
    echo 删除旧的build目录...
    rmdir /s /q "build" >nul 2>&1
)
if exist "*.spec" (
    echo 删除旧的spec文件...
    del "*.spec" >nul 2>&1
)
echo 成功: 环境清理完成

:: 检查必需文件
echo.
echo [2/6] 检查必需文件...
set "missing_files="
if not exist "launcher.py" set "missing_files=!missing_files! launcher.py"
if not exist "app.py" set "missing_files=!missing_files! app.py"
if not exist "init_db.py" set "missing_files=!missing_files! init_db.py"
if not exist "templates" set "missing_files=!missing_files! templates/"
if not exist "static" set "missing_files=!missing_files! static/"
if not exist "data" set "missing_files=!missing_files! data/"

if defined missing_files (
    echo 错误: 缺少必需文件: !missing_files!
    pause
    exit /b 1
)
echo 成功: 所有必需文件检查完成

:: 检查并创建最小化的数据目录
echo.
echo [3/6] 优化数据文件...
if not exist "data_minimal" mkdir "data_minimal"

:: 只复制必要的数据文件
copy "data\movies.csv" "data_minimal\" >nul 2>&1
copy "data\ratings.csv" "data_minimal\" >nul 2>&1
copy "data\links.csv" "data_minimal\" >nul 2>&1

:: 优化static目录 - 只包含必要文件
if not exist "static_minimal" mkdir "static_minimal"
if not exist "static_minimal\css" mkdir "static_minimal\css"
if not exist "static_minimal\js" mkdir "static_minimal\js"
if not exist "static_minimal\images" mkdir "static_minimal\images"

copy "static\css\*" "static_minimal\css\" >nul 2>&1
copy "static\js\*" "static_minimal\js\" >nul 2>&1
copy "static\images\logo.ico" "static_minimal\images\" >nul 2>&1
copy "static\images\logo.png" "static_minimal\images\" >nul 2>&1
copy "static\images\default-poster.jpg" "static_minimal\images\" >nul 2>&1

echo 成功: 数据文件优化完成

:: 执行精简打包
echo.
echo [4/6] 开始精简打包...
echo 这可能需要5-10分钟，请耐心等待...
echo.

pyinstaller ^
    --onedir ^
    --console ^
    --name "MovieHunter" ^
    --clean ^
    --noconfirm ^
    --exclude-module tkinter ^
    --exclude-module PyQt5 ^
    --exclude-module PyQt6 ^
    --exclude-module PySide2 ^
    --exclude-module PySide6 ^
    --exclude-module matplotlib ^
    --exclude-module scipy ^
    --exclude-module sklearn ^
    --exclude-module torch ^
    --exclude-module transformers ^
    --exclude-module jieba ^
    --exclude-module faiss ^
    --exclude-module faiss_cpu ^
    --exclude-module pyarrow ^
    --exclude-module numpy.distutils ^
    --exclude-module numpy.f2py ^
    --exclude-module pandas.plotting ^
    --exclude-module pandas.tests ^
    --exclude-module jupyter ^
    --exclude-module notebook ^
    --exclude-module IPython ^
    --exclude-module pytest ^
    --exclude-module unittest ^
    --exclude-module sqlite3 ^
    --exclude-module zmq ^
    --exclude-module pyzmq ^
    --exclude-module grpc ^
    --exclude-module asyncio ^
    --exclude-module aiohttp ^
    --exclude-module websockets ^
    --add-data "templates;templates" ^
    --add-data "static_minimal;static" ^
    --add-data "data_minimal;data" ^
    --add-data "schema.sql;." ^
    --add-data "requirements.txt;." ^
    --add-data "app.py;." ^
    --add-data "init_db.py;." ^
    --hidden-import "mysql.connector" ^
    --hidden-import "mysql.connector.pooling" ^
    --hidden-import "flask" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "numpy.core" ^
    --hidden-import "pandas.core" ^
    --hidden-import "hashlib" ^
    --hidden-import "secrets" ^
    --hidden-import "datetime" ^
    --hidden-import "decimal" ^
    launcher.py

if %errorlevel% neq 0 (
    echo.
    echo 错误: 打包失败
    echo 请检查错误信息并重试
    pause
    exit /b 1
)

:: 后处理优化
echo.
echo [5/6] 后处理优化...
if exist "dist\MovieHunter" (
    echo 复制额外文件...
    
    :: 确保核心文件在根目录
    copy "app.py" "dist\MovieHunter\" >nul 2>&1
    copy "launcher.py" "dist\MovieHunter\" >nul 2>&1
    copy "init_db.py" "dist\MovieHunter\" >nul 2>&1
    copy "*.md" "dist\MovieHunter\" >nul 2>&1
    
    :: 创建优化的启动脚本
    (
    echo @echo off
    echo title MovieHunter 精简版
    echo echo.
    echo echo ==========================================
    echo echo   MovieHunter 电影推荐系统 - 精简版
    echo echo ==========================================
    echo echo.
    echo echo 正在启动应用程序，请稍候...
    echo echo 当前目录: %%CD%%
    echo echo.
    echo cd /d "%%~dp0"
    echo echo 已切换到: %%CD%%
    echo echo.
    echo echo 检查文件...
    echo if not exist "MovieHunter.exe" ^(
    echo     echo 错误: 找不到 MovieHunter.exe!
    echo     pause
    echo     exit /b 1
    echo ^)
    echo echo 文件检查完成。启动 MovieHunter...
    echo echo.
    echo "MovieHunter.exe"
    echo echo.
    echo echo 应用程序已停止。
    echo pause
    ) > "dist\MovieHunter\启动_MovieHunter.bat"
    
    echo 成功: 后处理完成
) else (
    echo 错误: 打包失败，找不到输出目录
    pause
    exit /b 1
)

:: 检查最终大小
echo.
echo [6/6] 检查打包结果...
if exist "dist\MovieHunter" (
    echo 正在计算文件夹大小...
    powershell -Command "& {$size = (Get-ChildItem -Recurse 'dist\MovieHunter' | Measure-Object -Property Length -Sum).Sum / 1MB; Write-Host \"打包后大小: $([math]::Round($size, 2)) MB\"}"
) else (
    echo 警告: 无法检查文件夹大小
)

:: 清理临时文件
echo.
echo 清理临时文件...
if exist "data_minimal" rmdir /s /q "data_minimal" >nul 2>&1
if exist "static_minimal" rmdir /s /q "static_minimal" >nul 2>&1

echo.
echo ======================================================================================================
echo                                    精简打包完成！
echo ======================================================================================================
echo.
echo 打包结果:
echo    位置:         dist\MovieHunter\
echo    主程序:       MovieHunter.exe
echo    启动脚本:     启动_MovieHunter.bat
echo.
echo 优化说明:
echo    - 排除了大量不必要的库（PyQt5, torch, transformers等）
echo    - 只包含最少必要的数据文件
echo    - 优化了静态资源文件
echo    - 预计体积减少70-80%%
echo.
echo 使用说明:
echo    1. 将整个 dist\MovieHunter 文件夹打包分发
echo    2. 用户需要安装MySQL并启动服务
echo    3. 双击"启动_MovieHunter.bat"运行
echo.
echo 重要提示:
echo    - 首次启动可能需要30秒到1分钟，请耐心等待
echo    - 建议创建ZIP压缩包进行分发
echo    - 如有问题，请检查MySQL服务是否正常运行
echo ======================================================================================================

echo.
pause
