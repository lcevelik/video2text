@echo off
setlocal
title FonixFlow Setup & Run

echo ========================================================
echo FonixFlow - First Time Setup
echo ========================================================

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

:: 2. Create Venv
if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
)

:: 3. Activate Venv
call .venv\Scripts\activate.bat

:: 4. Install Dependencies
echo [INFO] Checking/Installing libraries (Whisper, PySide6, etc.)...
echo This may take a few minutes...
pip install -r requirements.txt >nul

:: 5. Check FFmpeg
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] FFmpeg not found.
    echo We need to download FFmpeg for audio processing.
    echo Please run: python scripts/dependency_manager.py
    :: For now, we try to run the app, it might prompt user.
)

:: 6. Run App
echo.
echo [INFO] Starting FonixFlow...
python app/fonixflow_qt.py
pause
