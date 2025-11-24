@echo off
REM Windows Build Script for FonixFlow
REM Creates a standalone single-file executable using PyInstaller

setlocal enabledelayedexpansion

echo ========================================
echo FonixFlow Windows Build Script
echo ========================================
echo.

REM Check if we're on Windows
if not "%OS%"=="Windows_NT" (
    echo Error: This script must be run on Windows
    exit /b 1
)

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not installed
    echo Download from: https://www.python.org/downloads/
    exit /b 1
)

echo [32m✓[0m Python version:
python --version
echo.

REM Check for ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [33m⚠ Warning: ffmpeg not found in PATH[0m
    echo   Install with chocolatey: choco install ffmpeg
    echo   Or download from: https://ffmpeg.org/download.html
    echo   Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH
    echo.
) else (
    echo [32m✓[0m ffmpeg found at:
    where ffmpeg
    echo.
)

REM Check for PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [33m⚠ PyInstaller not found. Installing...[0m
    pip install pyinstaller
    if errorlevel 1 (
        echo Error: Failed to install PyInstaller
        exit /b 1
    )
)

echo [32m✓[0m PyInstaller installed
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo [32m✓[0m Cleaned build directories
echo.

REM Build the executable
echo Building FonixFlow.exe...
echo This may take several minutes (5-10 min for first build)...
echo.

pyinstaller fonixflow_qt_windows.spec

REM Check if build was successful
if exist "dist\FonixFlow.exe" (
    echo.
    echo ========================================
    echo [32m✓ Build successful![0m
    echo ========================================
    echo.
    echo Your single-file executable is located at: dist\FonixFlow.exe
    echo.
    echo File size:
    dir "dist\FonixFlow.exe" | find "FonixFlow.exe"
    echo.
    echo To run:
    echo   dist\FonixFlow.exe
    echo.
    echo To distribute:
    echo   Copy dist\FonixFlow.exe to the user's computer
    echo   No installation required - just double-click to run!
    echo.
    echo Note: Windows Defender may scan the file on first run.
    echo This is normal for unsigned executables.
    echo.
) else (
    echo.
    echo ========================================
    echo [31m✗ Build failed![0m
    echo ========================================
    echo.
    echo Check the output above for errors.
    echo Common issues:
    echo   - ffmpeg not found: Install ffmpeg and add to PATH
    echo   - Missing dependencies: Run 'pip install -r requirements.txt'
    echo   - Permission errors: Run as Administrator or check antivirus
    echo.
    exit /b 1
)

echo ========================================
echo Build Information
echo ========================================
echo.
echo The single-file executable contains:
echo   - Python interpreter and all libraries
echo   - PySide6 Qt framework
echo   - PyTorch and OpenAI Whisper
echo   - FFmpeg binary for audio extraction
echo   - All application assets and translations
echo.
echo Whisper models are downloaded on first use.
echo Models are cached in: %%USERPROFILE%%\.cache\whisper
echo.
echo First launch may take 30-60 seconds as the app unpacks.
echo Subsequent launches are faster (~5-10 seconds).
echo.

endlocal
