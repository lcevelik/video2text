#!/bin/bash
# Script to create macOS .icns icon from PNG
# Usage: ./create_icns.sh

set -e

echo "Creating macOS .icns icon file..."

# Check if source PNG exists
if [ ! -f "assets/fonixflow_icon.png" ]; then
    echo "Error: assets/fonixflow_icon.png not found"
    exit 1
fi

# Create iconset directory
mkdir -p FonixFlow.iconset

# Generate all required icon sizes
echo "Generating icon sizes..."
sips -z 16 16     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_16x16.png
sips -z 32 32     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_16x16@2x.png
sips -z 32 32     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_32x32.png
sips -z 64 64     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_32x32@2x.png
sips -z 128 128   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_128x128.png
sips -z 256 256   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_128x128@2x.png
sips -z 256 256   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_256x256.png
sips -z 512 512   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_256x256@2x.png
sips -z 512 512   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_512x512.png
sips -z 1024 1024 assets/fonixflow_icon.png --out FonixFlow.iconset/icon_512x512@2x.png

# Create .icns file
echo "Creating .icns file..."
iconutil -c icns FonixFlow.iconset -o assets/fonixflow_icon.icns

# Clean up iconset directory
echo "Cleaning up..."
rm -rf FonixFlow.iconset

echo "✓ Successfully created assets/fonixflow_icon.icns"
