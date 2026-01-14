@echo off
title Voice Tool Launcher
cls

echo =======================================================
echo   GAMER ACCESSIBILITY TOOL - LAUNCHER
echo =======================================================

REM 1. Check if they have Python installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found!
    echo Please install Python from python.org and try again.
    echo.
    pause
    exit
)

REM 2. Check if libraries are installed (by checking for a marker file)
if exist "installed.marker" (
    echo [INFO] Libraries found. Skipping download.
    goto :RUN
)

echo.
echo [FIRST TIME SETUP]
echo This tool needs to download AI libraries (approx 2-3 GB).
echo This only happens ONCE. Please wait...
echo.

pip install -r requirements.txt

REM Create a marker file so we don't do this next time
echo installed > installed.marker
echo.
echo [SUCCESS] Installation complete!

:RUN
cls
echo Starting Voice Tool...
python "S to T.py"
pause