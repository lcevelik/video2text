#!/bin/bash

# Build script for FonixFlow Free Version (macOS)
# Usage: ./build_macos_free.sh

# Exit on error
set -e

APP_NAME="FonixFlow Free"
SPEC_FILE="fonixflow_free.spec"

echo "========================================"
echo "📦 Building FonixFlow Free Version (macOS)"
echo "========================================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Check for ffmpeg (required for runtime, but good to check here)
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: ffmpeg not found in PATH. Ensure it's installed/bundled."
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
rm -rf "$APP_NAME.app"

# Run PyInstaller
echo "Running PyInstaller..."
pyinstaller --noconfirm --clean "$SPEC_FILE"

# Verify build
if [ -d "dist/$APP_NAME.app" ]; then
    echo "✓ App bundle created: dist/$APP_NAME.app"
else
    echo "Error: App bundle not found!"
    exit 1
fi

# Create custom DMG with background and icon positioning
echo "Creating custom DMG package..."

DMG_NAME="FonixFlow_Free_macOS_Universal.dmg"

# Ensure DMG background exists
if [ ! -f "assets/dmg_background.png" ]; then
    echo "Creating DMG background..."
    ./scripts/create_dmg_background.sh assets/fonixflow_logo.png assets/dmg_background.png
fi

# Use custom DMG creator
./scripts/create_custom_dmg.sh "FonixFlow Free" "dist/FonixFlow Free.app" "dist/$DMG_NAME" "assets/dmg_background.png"

echo ""
echo "================================"
echo "✓ Free Version Build successful!"
echo "================================"
echo ""
echo "Your app is located at: dist/$APP_NAME.app"
echo "DMG package: dist/$DMG_NAME"
echo ""
