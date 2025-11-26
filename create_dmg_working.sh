#!/bin/bash
# Create a properly configured DMG for FonixFlow
# This version works around macOS permission issues

set -e

echo "========================================="
echo "Creating FonixFlow DMG Installer"
echo "========================================="

# Configuration matching your spec
DMG_NAME="FonixFlow"
DMG_VOLUME_NAME="FonixFlow Installer"
WINDOW_W=600
WINDOW_H=400
APP_ICON_X=150
APP_ICON_Y=200
APPS_LINK_X=450
APPS_LINK_Y=200

# Check if app exists
if [ ! -d "dist/FonixFlow.app" ]; then
    echo "❌ Error: dist/FonixFlow.app not found!"
    exit 1
fi

# Calculate DMG size (add 100MB overhead to be safe)
APP_SIZE=$(du -sm "dist/FonixFlow.app" | cut -f1)
DMG_SIZE_MB=$((APP_SIZE + 100))
echo "📦 App size: ${APP_SIZE}MB, DMG size: ${DMG_SIZE_MB}MB"

# Create temp directory for DMG contents
TEMP_DIR=$(mktemp -d -t fonixflow_dmg)
echo "📁 Temp directory: $TEMP_DIR"

# Copy app
echo "📋 Copying app..."
cp -R "dist/FonixFlow.app" "$TEMP_DIR/"

# Create Applications symlink
echo "🔗 Creating Applications symlink..."
ln -s /Applications "$TEMP_DIR/Applications"

# Create temporary read-write DMG
TEMP_DMG="$TEMP_DIR/rw.dmg"
echo "💿 Creating temporary DMG..."
hdiutil create -size ${DMG_SIZE_MB}m -fs HFS+ -volname "$DMG_VOLUME_NAME" "$TEMP_DMG" >/dev/null

# Mount it
echo "📂 Mounting DMG..."
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$TEMP_DMG" | egrep '^/dev/' | sed 1q | awk '{print $1}')
MOUNT_POINT="/Volumes/$DMG_VOLUME_NAME"

# Give it time to mount
sleep 2

# Copy contents
echo "📦 Copying contents to DMG..."
cp -R "$TEMP_DIR/FonixFlow.app" "$MOUNT_POINT/"
cp -R "$TEMP_DIR/Applications" "$MOUNT_POINT/"

# Set custom icon positions and window size using AppleScript
echo "🎨 Setting window layout..."
osascript <<EOF
tell application "Finder"
    tell disk "$DMG_VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, $((100+WINDOW_W)), $((100+WINDOW_H))}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set text size of viewOptions to 14
        delay 1
        set position of item "FonixFlow.app" of container window to {${APP_ICON_X}, ${APP_ICON_Y}}
        set position of item "Applications" of container window to {${APPS_LINK_X}, ${APPS_LINK_Y}}
        update without registering applications
        delay 2
        close
    end tell
end tell
EOF

# Wait for Finder to write changes
sleep 3

# Eject
echo "⏏️  Unmounting..."
hdiutil detach "$DEVICE" >/dev/null

# Convert to compressed read-only DMG
echo "🗜️  Compressing final DMG..."
hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg" >/dev/null

# Clean up
rm -rf "$TEMP_DIR"

# Show results
DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
echo ""
echo "========================================="
echo "✅ DMG created successfully!"
echo "========================================="
echo "📍 Location: dist/$DMG_NAME.dmg"
echo "📏 Size: $DMG_SIZE"
echo "🪟 Window: ${WINDOW_W}x${WINDOW_H}"
echo "📱 Icon positions configured"
echo ""
echo "To test: open dist/$DMG_NAME.dmg"
echo ""
