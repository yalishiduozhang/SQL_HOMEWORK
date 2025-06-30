Copying additional files...
@echo off
title MovieHunter
echo.
echo ======================================
echo MovieHunter Movie Recommendation System
echo ======================================
echo.
echo Starting application, please wait...
echo Current directory: %CD%
echo.
cd /d "%~dp0"
echo Changed to: %CD%
echo.
echo Checking files...
if not exist "MovieHunter.exe" (
    echo ERROR: MovieHunter.exe not found
    pause
    exit /b 1
)
echo Files OK. Starting MovieHunter...
echo.
"MovieHunter.exe"
echo.
echo Application stopped.
pause
