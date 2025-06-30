@echo off
chcp 65001 >nul
echo ======================================
echo MovieHunter Windows 安装包制作工具
echo ======================================
echo.

echo 正在检查必要文件...
set missing_files=0

echo 检查核心文件...
if not exist "app.py" (echo ✗ app.py 缺失 & set missing_files=1)
if not exist "init_db.py" (echo ✗ init_db.py 缺失 & set missing_files=1)
if not exist "schema.sql" (echo ✗ schema.sql 缺失 & set missing_files=1)
if not exist "requirements.txt" (echo ✗ requirements.txt 缺失 & set missing_files=1)

echo 检查启动脚本...
if not exist "MovieHunter启动器.bat" (echo ✗ 主启动器缺失 & set missing_files=1)
if not exist "start_windows.bat" (echo ✗ 初始化脚本缺失 & set missing_files=1)
if not exist "quick_start.bat" (echo ✗ 快速启动脚本缺失 & set missing_files=1)

echo 检查数据文件...
if not exist "data\movies.csv" (echo ⚠ movies.csv 缺失 - 应用可能无法正常工作)
if not exist "data\ratings.csv" (echo ⚠ ratings.csv 缺失 - 应用可能无法正常工作)

if %missing_files%==1 (
    echo.
    echo ✗ 有关键文件缺失，无法制作安装包
    pause
    exit /b 1
)

echo ✓ 文件检查完成

echo.
echo 创建发布文件夹...
if exist "MovieHunter_Windows" rmdir /s /q "MovieHunter_Windows"
mkdir "MovieHunter_Windows"

echo 复制核心文件...
copy "app.py" "MovieHunter_Windows\"
copy "init_db.py" "MovieHunter_Windows\"
copy "schema.sql" "MovieHunter_Windows\"
copy "requirements.txt" "MovieHunter_Windows\"

echo 复制启动脚本...
copy "MovieHunter启动器.bat" "MovieHunter_Windows\"
copy "start_windows.bat" "MovieHunter_Windows\"
copy "quick_start.bat" "MovieHunter_Windows\"
copy "check_environment.bat" "MovieHunter_Windows\"
copy "troubleshoot.bat" "MovieHunter_Windows\"
copy "config_template.bat" "MovieHunter_Windows\"

echo 复制文档...
copy "Windows启动指南.md" "MovieHunter_Windows\"
if exist "README.md" copy "README.md" "MovieHunter_Windows\"

echo 复制数据文件夹...
if exist "data" (
    xcopy "data" "MovieHunter_Windows\data\" /e /i /y
) else (
    mkdir "MovieHunter_Windows\data"
    echo 注意：data文件夹不存在，已创建空文件夹 > "MovieHunter_Windows\data\README.txt"
)

echo 复制静态资源...
if exist "static" (
    xcopy "static" "MovieHunter_Windows\static\" /e /i /y
) else (
    mkdir "MovieHunter_Windows\static"
    echo 注意：static文件夹不存在，已创建空文件夹 > "MovieHunter_Windows\static\README.txt"
)

echo 复制模板文件夹...
if exist "templates" (
    xcopy "templates" "MovieHunter_Windows\templates\" /e /i /y
) else (
    echo ⚠ templates文件夹不存在，应用可能无法正常工作
)

echo.
echo 创建快速开始说明...
echo MovieHunter Windows版 > "MovieHunter_Windows\快速开始.txt"
echo. >> "MovieHunter_Windows\快速开始.txt"
echo 使用步骤： >> "MovieHunter_Windows\快速开始.txt"
echo 1. 双击"MovieHunter启动器.bat" >> "MovieHunter_Windows\快速开始.txt"
echo 2. 首次使用选择"1"检查环境，然后选择"2"初始化 >> "MovieHunter_Windows\快速开始.txt"
echo 3. 日常使用选择"3"快速启动 >> "MovieHunter_Windows\快速开始.txt"
echo. >> "MovieHunter_Windows\快速开始.txt"
echo 测试账号：test / 123456 >> "MovieHunter_Windows\快速开始.txt"
echo 访问地址：http://localhost:6010 >> "MovieHunter_Windows\快速开始.txt"

echo.
echo ======================================
echo ✓ 安装包制作完成！
echo ======================================
echo.
echo 发布文件夹：MovieHunter_Windows
echo.
echo 用户使用说明：
echo 1. 将整个MovieHunter_Windows文件夹复制给用户
echo 2. 用户双击"MovieHunter启动器.bat"即可使用
echo 3. 首次使用需要按提示安装Python和MySQL
echo.
pause
