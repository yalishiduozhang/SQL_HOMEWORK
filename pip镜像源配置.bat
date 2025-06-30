@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title pip镜像源配置工具

echo ======================================
echo pip镜像源配置工具
echo ======================================
echo.
echo 此工具将为您配置pip镜像源，加速Python包下载
echo.

:: 检查pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ pip未安装或不可用
    echo 请先安装Python
    pause
    exit /b 1
)

echo 当前可用的镜像源：
echo.
echo 1. 清华大学镜像 (推荐)
echo    地址：https://pypi.tuna.tsinghua.edu.cn/simple
echo    特点：国内速度快，稳定性好
echo.
echo 2. 阿里云镜像
echo    地址：https://mirrors.aliyun.com/pypi/simple/
echo    特点：阿里云CDN，速度较快
echo.
echo 3. 豆瓣镜像
echo    地址：https://pypi.douban.com/simple/
echo    特点：老牌镜像，较稳定
echo.
echo 4. 中科大镜像
echo    地址：https://pypi.mirrors.ustc.edu.cn/simple/
echo    特点：教育网用户友好
echo.
echo 5. 华为云镜像
echo    地址：https://mirrors.huaweicloud.com/repository/pypi/simple/
echo    特点：企业级镜像，稳定
echo.
echo 0. 恢复官方源
echo.

set /p choice="请选择镜像源 (0-5): "

:: 创建pip配置目录
if not exist "%APPDATA%\pip" mkdir "%APPDATA%\pip"

if "%choice%"=="1" (
    set "mirror_url=https://pypi.tuna.tsinghua.edu.cn/simple"
    set "trusted_host=pypi.tuna.tsinghua.edu.cn"
    set "mirror_name=清华大学镜像"
) else if "%choice%"=="2" (
    set "mirror_url=https://mirrors.aliyun.com/pypi/simple/"
    set "trusted_host=mirrors.aliyun.com"
    set "mirror_name=阿里云镜像"
) else if "%choice%"=="3" (
    set "mirror_url=https://pypi.douban.com/simple/"
    set "trusted_host=pypi.douban.com"
    set "mirror_name=豆瓣镜像"
) else if "%choice%"=="4" (
    set "mirror_url=https://pypi.mirrors.ustc.edu.cn/simple/"
    set "trusted_host=pypi.mirrors.ustc.edu.cn"
    set "mirror_name=中科大镜像"
) else if "%choice%"=="5" (
    set "mirror_url=https://mirrors.huaweicloud.com/repository/pypi/simple/"
    set "trusted_host=mirrors.huaweicloud.com"
    set "mirror_name=华为云镜像"
) else if "%choice%"=="0" (
    if exist "%APPDATA%\pip\pip.ini" del "%APPDATA%\pip\pip.ini"
    echo.
    echo ✓ 已恢复pip官方源配置
    echo.
    goto :end
) else (
    echo.
    echo ✗ 无效选择
    pause
    exit /b 1
)

:: 写入配置文件
(
echo [global]
echo index-url = %mirror_url%
echo trusted-host = %trusted_host%
echo timeout = 120
echo [install]
echo trusted-host = %trusted_host%
) > "%APPDATA%\pip\pip.ini"

echo.
if exist "%APPDATA%\pip\pip.ini" (
    echo ✓ %mirror_name% 配置成功！
    echo   配置文件：%APPDATA%\pip\pip.ini
    echo   镜像地址：%mirror_url%
    echo.
    echo 测试镜像源连接...
    pip install --dry-run --quiet pip >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ 镜像源连接正常
    ) else (
        echo ⚠ 镜像源可能暂时不可用，但配置已保存
    )
) else (
    echo ✗ 配置文件创建失败
)

echo.
echo 您也可以临时使用镜像源安装包：
echo pip install 包名 -i %mirror_url% --trusted-host %trusted_host%
echo.
echo 示例：
echo pip install flask -i %mirror_url% --trusted-host %trusted_host%

:end
echo.
pause
