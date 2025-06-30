@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

title MovieHunter 启动器

echo.
echo     ===============================================================================
echo                                MovieHunter 启动器
echo     ===============================================================================
echo.
echo                                    Windows 一键启动器
echo.
echo ======================================================================================================

:menu
echo.
echo 请选择要执行的操作：
echo.
echo  【一键启动】
echo  0. 一键初始化和启动     - 全自动配置环境和启动（推荐新用户）
echo.
echo  【首次使用】
echo  1. 环境检查和安装指南    - 检查Python、MySQL等环境
echo  2. 完整初始化和启动      - 安装依赖、初始化数据库、启动应用
echo.
echo  【日常使用】
echo  3. 快速启动应用          - 直接启动应用（环境已配置）
echo.
echo  【维护工具】
echo  4. 故障排除工具          - 诊断和修复常见问题
echo  5. pip镜像源配置         - 配置加速下载的镜像源
echo  6. 测试镜像源速度        - 测试各镜像源连接速度
echo  7. 查看启动指南          - 打开使用说明文档
echo.
echo  【高级功能】
echo  8. 打包为EXE文件        - 生成独立的可执行文件
echo.
echo  9. 退出程序
echo.
echo ======================================================================================================
set /p choice="请输入选项编号 (0-8,9): "

if "%choice%"=="0" goto one_click_start
if "%choice%"=="1" goto env_check
if "%choice%"=="2" goto full_init
if "%choice%"=="3" goto quick_start
if "%choice%"=="4" goto troubleshoot
if "%choice%"=="5" goto pip_config
if "%choice%"=="6" goto test_mirrors
if "%choice%"=="7" goto show_guide
if "%choice%"=="8" goto pack_exe
if "%choice%"=="9" goto exit
echo.
echo ✗ 无效选项，请重新输入
goto menu

:one_click_start
echo.
echo ======================================
echo 启动一键初始化和启动程序...
echo ======================================
if exist "一键启动.bat" (
    call "一键启动.bat"
) else (
    echo ✗ 一键启动.bat 文件不存在
    pause
)
goto menu

:env_check
echo.
echo ======================================
echo 启动环境检查工具...
echo ======================================
if exist "check_environment.bat" (
    call check_environment.bat
) else (
    echo ✗ check_environment.bat 文件不存在
    pause
)
goto menu

:full_init
echo.
echo ======================================
echo 启动完整初始化程序...
echo ======================================
if exist "start_windows.bat" (
    call start_windows.bat
) else (
    echo ✗ start_windows.bat 文件不存在
    pause
)
goto menu

:quick_start
echo.
echo ======================================
echo 启动快速启动程序...
echo ======================================
if exist "quick_start.bat" (
    call quick_start.bat
) else (
    echo ✗ quick_start.bat 文件不存在
    pause
)
goto menu

:troubleshoot
echo.
echo ======================================
echo 启动故障排除工具...
echo ======================================
if exist "troubleshoot.bat" (
    call troubleshoot.bat
) else (
    echo ✗ troubleshoot.bat 文件不存在
    pause
)
goto menu

:pip_config
echo.
echo ======================================
echo 启动pip镜像源配置工具...
echo ======================================
if exist "pip镜像源配置.bat" (
    call "pip镜像源配置.bat"
) else (
    echo ✗ pip镜像源配置.bat 文件不存在
    pause
)
goto menu

:test_mirrors
echo.
echo ======================================
echo 启动镜像源速度测试工具...
echo ======================================
if exist "测试镜像源速度.bat" (
    call "测试镜像源速度.bat"
) else (
    echo ✗ 测试镜像源速度.bat 文件不存在
    pause
)
goto menu

:pack_exe
echo.
echo ======================================
echo 启动EXE打包工具...
echo ======================================
if exist "打包exe.bat" (
    call "打包exe.bat"
) else (
    echo ✗ 打包exe.bat 文件不存在
    pause
)
goto menu

:show_guide
echo.
echo ======================================
echo 打开使用指南...
echo ======================================
if exist "Windows启动指南.md" (
    start notepad "Windows启动指南.md"
) else (
    echo ✗ Windows启动指南.md 文件不存在
    echo.
    echo 基本使用说明：
    echo 1. 首次使用请选择"环境检查"确保系统环境正确
    echo 2. 然后选择"完整初始化"安装依赖和初始化数据库
    echo 3. 日常使用直接选择"快速启动"即可
    echo 4. 遇到问题使用"故障排除工具"
    pause
)
goto menu

:exit
echo.
echo ======================================
echo 感谢使用 MovieHunter！
echo ======================================
echo.
echo 如有问题，请：
echo 1. 使用故障排除工具进行诊断
echo 2. 查看Windows启动指南.md文档
echo 3. 检查项目README.md获取更多帮助
echo.
echo 再见！
timeout /t 3 >nul
exit /b 0
