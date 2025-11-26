#!/bin/bash
# Linux Build Script for FonixFlow
# Creates a standalone executable using PyInstaller

set -e  # Exit on error

echo "================================"
echo "FonixFlow Linux Build Script"
echo "================================"
echo ""

# Check if we're on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "linux"* ]]; then
    echo "Error: This script must be run on Linux"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    echo "Install with: sudo apt-get install python3 python3-pip  (Debian/Ubuntu)"
    echo "              sudo yum install python3 python3-pip      (RHEL/CentOS)"
    exit 1
fi

echo "✓ Python version: $(python3 --version)"

# Check for pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "Error: pip is required but not installed"
    echo "Install with: sudo apt-get install python3-pip  (Debian/Ubuntu)"
    exit 1
fi

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ Warning: ffmpeg not found"
    echo "  Install with: sudo apt-get install ffmpeg  (Debian/Ubuntu)"
    echo "                sudo yum install ffmpeg        (RHEL/CentOS)"
    echo "                sudo pacman -S ffmpeg         (Arch)"
    echo ""
    echo "  The app will still build, but audio/video processing may not work."
    echo ""
else
    echo "✓ ffmpeg found at: $(which ffmpeg)"
fi

# Check for libxcb-cursor (required for Qt 6.5+)
if [ ! -f "/usr/lib/x86_64-linux-gnu/libxcb-cursor.so.0" ] && \
   [ ! -f "/usr/lib/x86_64-linux-gnu/libxcb-cursor.so" ] && \
   [ ! -f "/usr/lib/libxcb-cursor.so.0" ]; then
    echo "⚠ Warning: libxcb-cursor not found"
    echo "  Install with: sudo apt-get install libxcb-cursor0  (Debian/Ubuntu)"
    echo "  This library is required for Qt xcb platform plugin on Qt 6.5+"
    echo "  The app may not start without it."
    echo ""
else
    echo "✓ libxcb-cursor found"
fi

# Check for PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "⚠ PyInstaller not found. Installing..."
    python3 -m pip install --user pyinstaller || pip3 install --user pyinstaller
fi

echo "✓ PyInstaller installed"

# Check if requirements are installed
echo ""
echo "Checking Python dependencies..."
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "⚠ Some dependencies may be missing. Installing from requirements.txt..."
    python3 -m pip install --break-system-packages -r requirements.txt 2>&1 | tail -3 || \
    python3 -m pip install --user -r requirements.txt 2>&1 | tail -3 || \
    pip3 install --user -r requirements.txt 2>&1 | tail -3
else
    echo "✓ Dependencies appear to be installed"
fi

# Try to download libxcb-cursor package if not installed
if [ ! -f "/usr/lib/x86_64-linux-gnu/libxcb-cursor.so.0" ] && \
   [ ! -f "/usr/lib/x86_64-linux-gnu/libxcb-cursor.so" ] && \
   [ ! -f "/usr/lib/libxcb-cursor.so.0" ]; then
    echo ""
    echo "Attempting to download libxcb-cursor package for bundling..."
    cd /tmp
    apt download libxcb-cursor0 2>/dev/null && \
    dpkg-deb -x libxcb-cursor0*.deb /tmp/xcb-cursor-extract 2>/dev/null && \
    echo "✓ Downloaded libxcb-cursor package" || \
    echo "⚠ Could not download package (may need sudo for apt download)"
    cd - > /dev/null
fi

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist
echo "✓ Cleaned build directories"

# Build the app
echo ""
echo "Building FonixFlow..."
echo "This may take several minutes..."
echo ""

pyinstaller fonixflow_qt_linux.spec

# Check if build was successful
if [ -d "dist/FonixFlow" ]; then
    echo ""
    echo "================================"
    echo "✓ Build successful!"
    echo "================================"
    echo ""
    echo "Your app is located at: dist/FonixFlow/"
    echo ""
    echo "To run the application:"
    echo "  ./dist/FonixFlow/FonixFlow"
    echo ""
    echo "To create a desktop entry, you can create a .desktop file:"
    echo ""
    cat << 'EOF'
Create ~/.local/share/applications/fonixflow.desktop with:
[Desktop Entry]
Name=FonixFlow
Comment=Audio and Video Transcription Tool
Exec=/path/to/dist/FonixFlow/FonixFlow
Icon=/path/to/dist/FonixFlow/assets/fonixflow_icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Video;
EOF
    echo ""
else
    echo ""
    echo "================================"
    echo "✗ Build failed!"
    echo "================================"
    echo ""
    echo "Check the output above for errors."
    exit 1
fi

