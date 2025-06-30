@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ======================================
echo MovieHunter 故障排除工具
echo ======================================
echo.

:menu
echo 请选择要执行的操作：
echo.
echo 1. 检查系统环境
echo 2. 重新安装Python依赖
echo 3. 测试数据库连接
echo 4. 重置数据库
echo 5. 清理临时文件
echo 6. 查看端口占用
echo 7. 生成诊断报告
echo 0. 退出
echo.
set /p choice="请输入选项 (0-7): "

if "%choice%"=="1" goto check_env
if "%choice%"=="2" goto reinstall_deps
if "%choice%"=="3" goto test_db
if "%choice%"=="4" goto reset_db
if "%choice%"=="5" goto cleanup
if "%choice%"=="6" goto check_ports
if "%choice%"=="7" goto diagnosis
if "%choice%"=="0" goto exit
goto menu

:check_env
echo.
echo ======================================
echo 检查系统环境
echo ======================================
echo.
echo [Python检查]
python --version 2>nul
if %errorlevel% neq 0 (
    echo ✗ Python未安装或未添加到PATH
) else (
    echo ✓ Python已安装
)

echo.
echo [pip检查]
pip --version 2>nul
if %errorlevel% neq 0 (
    echo ✗ pip不可用
) else (
    echo ✓ pip可用
)

echo.
echo [MySQL检查]
sc query mysql 2>nul | find "RUNNING" >nul
if %errorlevel% neq 0 (
    echo ✗ MySQL服务未运行
) else (
    echo ✓ MySQL服务正在运行
)

echo.
echo [文件检查]
if exist "app.py" (echo ✓ app.py存在) else (echo ✗ app.py不存在)
if exist "requirements.txt" (echo ✓ requirements.txt存在) else (echo ✗ requirements.txt不存在)
if exist "schema.sql" (echo ✓ schema.sql存在) else (echo ✗ schema.sql不存在)
if exist "init_db.py" (echo ✓ init_db.py存在) else (echo ✗ init_db.py不存在)
if exist "data\movies.csv" (echo ✓ movies.csv存在) else (echo ✗ movies.csv不存在)

pause
goto menu

:reinstall_deps
echo.
echo ======================================
echo 重新安装Python依赖
echo ======================================
echo.
echo 1. 升级pip...
python -m pip install --upgrade pip
echo.
echo 2. 清理pip缓存...
pip cache purge
echo.
echo 3. 重新安装依赖包...
pip uninstall -y flask numpy pandas mysql-connector-python pillow
pip install -r requirements.txt
echo.
echo 依赖重新安装完成
pause
goto menu

:test_db
echo.
echo ======================================
echo 测试数据库连接
echo ======================================
echo.
echo 创建数据库连接测试脚本...
echo import mysql.connector > test_db_temp.py
echo from mysql.connector import Error >> test_db_temp.py
echo import getpass >> test_db_temp.py
echo. >> test_db_temp.py
echo try: >> test_db_temp.py
echo     password = getpass.getpass("请输入MySQL密码: ") >> test_db_temp.py
echo     connection = mysql.connector.connect( >> test_db_temp.py
echo         host='localhost', >> test_db_temp.py
echo         user='root', >> test_db_temp.py
echo         password=password >> test_db_temp.py
echo     ) >> test_db_temp.py
echo     if connection.is_connected(): >> test_db_temp.py
echo         print("✓ 数据库连接成功") >> test_db_temp.py
echo         connection.close() >> test_db_temp.py
echo except Error as e: >> test_db_temp.py
echo     print(f"✗ 数据库连接失败: {e}") >> test_db_temp.py

python test_db_temp.py
del test_db_temp.py
pause
goto menu

:reset_db
echo.
echo ======================================
echo 重置数据库
echo ======================================
echo.
echo 警告：这将删除所有现有数据！
set /p confirm="确认要重置数据库吗？ (yes/N): "
if not "%confirm%"=="yes" (
    echo 操作已取消
    pause
    goto menu
)

echo 正在重置数据库...
python init_db.py
echo 数据库重置完成
pause
goto menu

:cleanup
echo.
echo ======================================
echo 清理临时文件
echo ======================================
echo.
echo 清理Python缓存...
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.pyc" del /q "*.pyc"

echo 清理pip缓存...
pip cache purge 2>nul

echo 清理临时文件完成
pause
goto menu

:check_ports
echo.
echo ======================================
echo 检查端口占用
echo ======================================
echo.
echo 检查端口6010（Web应用）...
netstat -an | find ":6010" 2>nul
if %errorlevel% neq 0 (
    echo ✓ 端口6010未被占用
) else (
    echo ⚠ 端口6010已被占用
)

echo.
echo 检查端口3306（MySQL）...
netstat -an | find ":3306" 2>nul
if %errorlevel% neq 0 (
    echo ✗ 端口3306未被占用（MySQL可能未启动）
) else (
    echo ✓ 端口3306已被占用（MySQL正在运行）
)

echo.
echo 显示所有监听端口...
netstat -an | find "LISTENING"
pause
goto menu

:diagnosis
echo.
echo ======================================
echo 生成诊断报告
echo ======================================
echo.
echo 正在生成诊断报告...

echo MovieHunter 诊断报告 > diagnosis.txt
echo 生成时间: %date% %time% >> diagnosis.txt
echo. >> diagnosis.txt

echo ========== 系统信息 ========== >> diagnosis.txt
systeminfo | find "OS Name" >> diagnosis.txt
systeminfo | find "OS Version" >> diagnosis.txt
echo. >> diagnosis.txt

echo ========== Python环境 ========== >> diagnosis.txt
python --version 2>>diagnosis.txt
pip --version 2>>diagnosis.txt
echo. >> diagnosis.txt

echo ========== 已安装包 ========== >> diagnosis.txt
pip list 2>>diagnosis.txt
echo. >> diagnosis.txt

echo ========== MySQL服务 ========== >> diagnosis.txt
sc query mysql 2>>diagnosis.txt
echo. >> diagnosis.txt

echo ========== 端口占用 ========== >> diagnosis.txt
netstat -an | find ":6010" >> diagnosis.txt 2>&1
netstat -an | find ":3306" >> diagnosis.txt 2>&1
echo. >> diagnosis.txt

echo ========== 文件检查 ========== >> diagnosis.txt
dir /b *.py >> diagnosis.txt 2>&1
dir /b *.sql >> diagnosis.txt 2>&1
dir /b data\*.csv >> diagnosis.txt 2>&1

echo.
echo ✓ 诊断报告已保存到 diagnosis.txt
echo 如需技术支持，请提供此文件
pause
goto menu

:exit
echo.
echo 再见！
pause
exit /b 0
