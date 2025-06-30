@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title 镜像源速度测试

echo ======================================
echo pip镜像源速度测试工具
echo ======================================
echo.

:: 定义镜像源
set "mirrors[0]=https://pypi.tuna.tsinghua.edu.cn/simple pypi.tuna.tsinghua.edu.cn 清华大学"
set "mirrors[1]=https://mirrors.aliyun.com/pypi/simple/ mirrors.aliyun.com 阿里云"
set "mirrors[2]=https://pypi.douban.com/simple/ pypi.douban.com 豆瓣"
set "mirrors[3]=https://pypi.mirrors.ustc.edu.cn/simple/ pypi.mirrors.ustc.edu.cn 中科大"
set "mirrors[4]=https://mirrors.huaweicloud.com/repository/pypi/simple/ mirrors.huaweicloud.com 华为云"

echo 正在测试各镜像源的连接速度...
echo.

for /L %%i in (0,1,4) do (
    for /f "tokens=1,2,3" %%a in ("!mirrors[%%i]!") do (
        echo 测试 %%c 镜像源...
        
        :: 使用curl测试连接速度（如果有curl）
        curl --version >nul 2>&1
        if !errorlevel! equ 0 (
            for /f %%t in ('powershell -command "Measure-Command { curl -s -o nul %%a 2>nul } | Select-Object -ExpandProperty TotalMilliseconds"') do (
                if %%t lss 1000 (
                    echo   ✓ %%c: %%t ms ^(很快^)
                ) else if %%t lss 3000 (
                    echo   ✓ %%c: %%t ms ^(正常^)
                ) else if %%t lss 10000 (
                    echo   ⚠ %%c: %%t ms ^(较慢^)
                ) else (
                    echo   ✗ %%c: 超时或连接失败
                )
            )
        ) else (
            :: 如果没有curl，使用ping测试主机
            for /f "tokens=2 delims=/" %%h in ("%%b") do (
                ping -n 1 %%h >nul 2>&1
                if !errorlevel! equ 0 (
                    echo   ✓ %%c: 连接正常
                ) else (
                    echo   ✗ %%c: 连接失败
                )
            )
        )
    )
)

echo.
echo ======================================
echo 测试完成！
echo ======================================
echo.
echo 建议选择连接速度最快的镜像源进行配置
echo 可以使用 pip镜像源配置.bat 进行配置
echo.
pause
