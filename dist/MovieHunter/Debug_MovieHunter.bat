@echo off
title MovieHunter Debug
echo Starting MovieHunter in debug mode...
cd /d "%~dp0"
echo Current directory: %CD%
echo.
echo Listing files:
dir /b
echo.
echo Starting application...
"MovieHunter.exe"
echo.
echo Debug session ended.
pause
