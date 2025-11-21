@echo off
REM Modern Qt GUI Launcher for Windows

echo ========================================
echo FonixFlow - Modern Qt Interface
echo ========================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    echo.
    pause
    exit /b 1
)

REM Display Python version
echo Checking Python version...
python --version
echo.

REM Check if PySide6 is installed
python -c "import PySide6" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PySide6 not found. Installing...
    pip install PySide6>=6.6.0
    echo.
)

REM Launch the Qt application
echo Starting Modern Qt Interface...
echo.
python -m app.fonixflow_qt

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo Check the logs folder for details.
)

echo.
pause
