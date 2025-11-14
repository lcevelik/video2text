@echo off
REM Enhanced Video to Text Launcher for Windows
REM This script launches the enhanced version of the application

echo ========================================
echo Video/Audio to Text - Enhanced Version
echo ========================================
echo.

REM Refresh PATH to include newly installed programs
call refreshenv >nul 2>&1

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Checking Python version...
python --version
echo.

REM Check if required files exist
if not exist "main_enhanced.py" (
    echo ERROR: main_enhanced.py not found!
    echo Make sure you're running this script from the correct directory.
    echo.
    pause
    exit /b 1
)

REM Launch the application
echo Starting application...
echo.
python main_enhanced.py

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo Check the logs folder for details.
)

echo.
pause
