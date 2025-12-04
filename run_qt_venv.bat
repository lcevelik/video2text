@echo off
REM Modern Qt GUI Launcher for Windows (using virtual environment)

echo ========================================
echo FonixFlow - Modern Qt Interface (VENV)
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run run_light.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

REM Display Python version from venv
echo Checking Python version (from venv)...
.venv\Scripts\python.exe --version
echo.

REM Check if PySide6 is installed in venv
.venv\Scripts\python.exe -c "import PySide6" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PySide6 not found in venv. Installing...
    .venv\Scripts\pip.exe install PySide6>=6.6.0
    echo.
)

REM Launch the Qt application using venv Python
echo Starting Modern Qt Interface (using virtual environment)...
echo.
.venv\Scripts\python.exe -m app.fonixflow_qt

REM Check exit code
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo Check the logs folder for details.
)

echo.
pause

