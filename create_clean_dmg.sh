#!/bin/bash
# Create a clean DMG without temporary folders

set -e

echo "Creating clean DMG for FonixFlow..."

# Configuration
DMG_NAME="FonixFlow"
VOLUME_NAME="FonixFlow Installer"
APP_PATH="dist/FonixFlow.app"
DMG_PATH="dist/${DMG_NAME}.dmg"

# Clean up any existing DMG
rm -f "${DMG_PATH}"
hdiutil detach "/Volumes/${VOLUME_NAME}" 2>/dev/null || true

# Create temporary directory
TMP_DIR=$(mktemp -d)
trap "rm -rf ${TMP_DIR}" EXIT

# Copy app to temp directory
echo "Copying app..."
cp -R "${APP_PATH}" "${TMP_DIR}/"

# Create Applications symlink
ln -s /Applications "${TMP_DIR}/Applications"

# Create DMG from folder
echo "Creating DMG..."
hdiutil create -volname "${VOLUME_NAME}" \
    -srcfolder "${TMP_DIR}" \
    -ov -format UDZO \
    -fs HFS+ \
    -imagekey zlib-level=9 \
    "${DMG_PATH}"

echo ""
echo "✓ Clean DMG created: ${DMG_PATH}"
echo "Size: $(du -h ${DMG_PATH} | cut -f1)"
