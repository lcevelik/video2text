@echo off
REM Windows Build Script for FonixFlow
REM Creates a standalone executable using PyInstaller

setlocal enabledelayedexpansion

echo ================================
echo FonixFlow Windows Build Script
echo ================================
echo.

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is required but not installed
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    exit /b 1
)

echo [92m✓[0m Python version:
python --version
echo.

REM Check for ffmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [93m⚠ Warning: ffmpeg not found in PATH[0m
    echo   Download from: https://ffmpeg.org/download.html#build-windows
    echo   Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH
    echo.
) else (
    echo [92m✓[0m ffmpeg found at:
    where ffmpeg
    echo.
)

REM Check for PyInstaller
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo [93m⚠ PyInstaller not found. Installing...[0m
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Error: Failed to install PyInstaller
        exit /b 1
    )
)

echo [92m✓[0m PyInstaller installed
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [92m✓[0m Cleaned build directories
echo.

REM Build the app
echo Building FonixFlow.exe...
echo This may take several minutes...
echo.

pyinstaller fonixflow_qt_windows.spec

REM Check if build was successful
if exist "dist\FonixFlow\FonixFlow.exe" (
    echo.
    echo ================================
    echo [92m✓ Build successful![0m
    echo ================================
    echo.
    echo Your application is located at: dist\FonixFlow\
    echo.
    echo To run:
    echo   dist\FonixFlow\FonixFlow.exe
    echo.
    echo To create an installer, use Inno Setup or NSIS
    echo See BUILD_WINDOWS.md for details
    echo.
) else (
    echo.
    echo ================================
    echo [91m✗ Build failed![0m
    echo ================================
    echo.
    echo Check the output above for errors.
    exit /b 1
)
