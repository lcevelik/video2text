#!/bin/bash
# macOS Light Build Script

echo "========================================================"
echo "FonixFlow Light Installer (macOS)"
echo "========================================================"

# Create dist folder
rm -rf FonixFlow_Light_Mac
mkdir -p FonixFlow_Light_Mac

# Copy source
echo "Copying source..."
cp -r app gui transcription assets i18n tools scripts requirements.txt FonixFlow_Light_Mac/
cp run_light.sh FonixFlow_Light_Mac/
chmod +x FonixFlow_Light_Mac/run_light.sh

# Create ZIP
echo "Creating ZIP..."
zip -r FonixFlow_Light_Mac.zip FonixFlow_Light_Mac

echo ""
echo "Build Complete!"
echo "Distribution file: FonixFlow_Light_Mac.zip"
echo "Unzip this file and run './run_light.sh' to install dependencies and start."
