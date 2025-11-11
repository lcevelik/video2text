@echo off
REM Video to Text - Application Launcher (Batch file)
REM This script refreshes the PATH and launches the application

REM Refresh PATH
call refreshenv >nul 2>&1

REM Try to run Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH.
    echo Please close and reopen this terminal, or restart your computer.
    echo.
    echo Alternatively, try using the Python launcher:
    py main.py
    pause
    exit /b 1
)

echo Starting Video to Text application...
echo.
python main.py
pause

