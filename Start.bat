@echo off
title Voice Tool Launcher
echo =================================================
echo  Checking for updates and libraries...
echo =================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please download Python from python.org
    pause
    exit
)

REM Install the shopping list (Only runs if missing)
echo Installing/Verifying AI libraries... (This may take time on first run)
pip install -r requirements.txt

REM Clear screen and run your tool
cls
echo Starting the tool...
python "S to T.py"

pause