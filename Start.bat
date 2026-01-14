@echo off
title Gamer Accessibility Tool - Installer
color 0b
cls

echo =======================================================
echo    GAMER ACCESSIBILITY TOOL (Version 1.1)
echo =======================================================
echo.

REM --- 1. CHECK FOR PYTHON ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0c
    echo [ERROR] Python is not installed!
    echo.
    echo To use this tool, you need Python.
    echo I am opening the download page for you now...
    echo.
    echo 1. Download the "Windows Installer (64-bit)"
    echo 2. IMPORTANT: Check the box "Add Python to PATH" during install.
    echo 3. Run this file again after installing.
    echo.
    timeout /t 5 >nul
    start https://www.python.org/downloads/
    pause
    exit
)

REM --- 2. INSTALL LIBRARIES (Only runs if missing) ---
if exist "installed.marker" goto :RUN

echo [FIRST TIME SETUP]
echo We need to download the AI brain (PyTorch & Whisper).
echo This is about 2-3 GB. It depends on your internet speed.
echo Please wait...
echo.
pip install -r requirements.txt

REM Mark as installed so we don't do this next time
echo installed > installed.marker
echo.
echo [SUCCESS] Download complete!

:RUN
REM --- 3. RUN THE TOOL ---
cls
echo Starting Voice Tool...
python "S to T.py"
pause
