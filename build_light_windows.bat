@echo off
setlocal

echo ========================================================
echo FonixFlow Light Installer (Windows)
echo ========================================================

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

:: Create virtual environment if missing
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate venv
call .venv\Scripts\activate.bat

:: Install dependencies
echo Checking dependencies...
pip install -r requirements.txt
pip install pyinstaller

:: Build the 'Light' Launcher
:: We exclude heavy libraries so the EXE is small.
:: The EXE will rely on the local python environment or check for it.
:: ACTUALLY: For a purely 'light' distribution, we don't freeze the app.
:: We provide a runner script.

echo.
echo Packaging source code...
if exist "FonixFlow_Light_Windows" rmdir /s /q "FonixFlow_Light_Windows"
mkdir "FonixFlow_Light_Windows"

:: Copy source files
xcopy /E /I /Y "app" "FonixFlow_Light_Windows\app"
xcopy /E /I /Y "gui" "FonixFlow_Light_Windows\gui"
xcopy /E /I /Y "transcription" "FonixFlow_Light_Windows\transcription"
xcopy /E /I /Y "assets" "FonixFlow_Light_Windows\assets"
xcopy /E /I /Y "i18n" "FonixFlow_Light_Windows\i18n"
xcopy /E /I /Y "tools" "FonixFlow_Light_Windows\tools"
xcopy /E /I /Y "scripts" "FonixFlow_Light_Windows\scripts"
copy "requirements.txt" "FonixFlow_Light_Windows\"
copy "run_light.bat" "FonixFlow_Light_Windows\"

:: Create a ZIP (using PowerShell)
echo Zipping...
powershell Compress-Archive -Path "FonixFlow_Light_Windows" -DestinationPath "FonixFlow_Light_Windows.zip" -Force

echo.
echo Build Complete!
echo Distribution file: FonixFlow_Light_Windows.zip
echo Unzip this file and run 'run_light.bat' to install dependencies and start.
pause
