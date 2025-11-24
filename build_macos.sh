#!/bin/bash
# macOS Build Script for FonixFlow
# Creates a standalone .app bundle using PyInstaller

set -e  # Exit on error

echo "================================"
echo "FonixFlow macOS Build Script"
echo "================================"
echo ""

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    echo "Install with: brew install python@3.11"
    exit 1
fi

echo "✓ Python version: $(python3 --version)"

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ Warning: ffmpeg not found"
    echo "  Install with: brew install ffmpeg"
    echo ""
else
    echo "✓ ffmpeg found at: $(which ffmpeg)"
fi

# Check for PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "⚠ PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

echo "✓ PyInstaller installed"

# Create .icns icon if it doesn't exist
if [ ! -f "assets/fonixflow_icon.icns" ]; then
    echo ""
    echo "Creating .icns icon file..."
    if [ -f "create_icns.sh" ]; then
        ./create_icns.sh
    else
        echo "⚠ Warning: create_icns.sh not found, will use PNG icon"
    fi
fi

# Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist
echo "✓ Cleaned build directories"

# Build the app
echo ""
echo "Building FonixFlow.app..."
echo "This may take several minutes..."
echo ""

pyinstaller fonixflow_qt.spec

# Check if build was successful
if [ -d "dist/FonixFlow.app" ]; then
    echo ""
    echo "================================"
    echo "✓ Build successful!"
    echo "================================"
    echo ""

    # Get app size
    APP_SIZE=$(du -sh dist/FonixFlow.app | awk '{print $1}')
    echo "App bundle size: $APP_SIZE"
    echo "Location: dist/FonixFlow.app"
    echo ""

    # Check if ffmpeg is bundled
    if [ -f "dist/FonixFlow.app/Contents/MacOS/ffmpeg" ]; then
        echo "✓ ffmpeg bundled successfully"
    else
        echo "⚠ Warning: ffmpeg not found in bundle"
        echo "  The app may not be able to extract audio from video files"
    fi
    echo ""

    echo "To install:"
    echo "  cp -r dist/FonixFlow.app /Applications/"
    echo ""
    echo "To run directly:"
    echo "  open dist/FonixFlow.app"
    echo ""

    # Create custom DMG with background and icon positioning
    echo "Creating custom DMG package..."

    DMG_NAME="FonixFlow_macOS_Universal.dmg"

    # Ensure DMG background exists
    if [ ! -f "assets/dmg_background.png" ]; then
        echo "Creating DMG background..."
        if [ -f "./scripts/create_dmg_background.sh" ]; then
            ./scripts/create_dmg_background.sh assets/fonixflow_logo.png assets/dmg_background.png
        else
            echo "⚠ Warning: create_dmg_background.sh not found, DMG will have no background"
        fi
    fi

    # Use custom DMG creator
    if [ -f "./scripts/create_custom_dmg.sh" ]; then
        ./scripts/create_custom_dmg.sh "FonixFlow" "dist/FonixFlow.app" "dist/$DMG_NAME" "assets/dmg_background.png"
    else
        echo "⚠ Warning: create_custom_dmg.sh not found, creating basic DMG..."
        hdiutil create -volname "FonixFlow" -srcfolder "dist/FonixFlow.app" -ov -format UDZO "dist/$DMG_NAME"
        if [ -f "dist/$DMG_NAME" ]; then
            echo "✓ Basic DMG created: dist/$DMG_NAME"
        fi
    fi
    
    # Optional: Code sign the app (requires Apple Developer ID)
    if [ ! -z "$CODESIGN_IDENTITY" ]; then
        echo "Code signing with identity: $CODESIGN_IDENTITY"
        codesign --deep --force --verify --verbose --sign "$CODESIGN_IDENTITY" \
                 --options runtime \
                 --entitlements entitlements.plist \
                 dist/FonixFlow.app
        echo "✓ Code signing complete"
    else
        echo "Note: App is not code signed. To sign, set CODESIGN_IDENTITY environment variable:"
        echo "  export CODESIGN_IDENTITY='Developer ID Application: Your Name (TEAMID)'"
        echo "  ./build_macos.sh"
    fi
else
    echo ""
    echo "================================"
    echo "✗ Build failed!"
    echo "================================"
    echo ""
    echo "Check the output above for errors."
    exit 1
fi
