#!/bin/bash

# Custom DMG Creator for FonixFlow
# Creates a beautifully styled DMG with custom background and icon positioning

set -e

APP_NAME="$1"
APP_PATH="$2"
DMG_NAME="$3"
BACKGROUND_IMG="$4"

if [ -z "$APP_NAME" ] || [ -z "$APP_PATH" ] || [ -z "$DMG_NAME" ]; then
    echo "Usage: $0 <app_name> <app_path> <dmg_name> [background_image]"
    echo "Example: $0 'FonixFlow' 'dist/FonixFlow.app' 'dist/FonixFlow.dmg' 'assets/dmg_background.png'"
    exit 1
fi

if [ ! -d "$APP_PATH" ]; then
    echo "Error: App not found at $APP_PATH"
    exit 1
fi

# Set default background if not provided
if [ -z "$BACKGROUND_IMG" ]; then
    BACKGROUND_IMG="assets/dmg_background.png"
fi

echo "=========================================="
echo "Creating Custom DMG: $DMG_NAME"
echo "=========================================="

# Create temporary directory
TMP_DIR=$(mktemp -d)
DMG_MOUNT_NAME="$APP_NAME Installer"

echo "Preparing DMG contents..."

# Copy app to temp directory
cp -R "$APP_PATH" "$TMP_DIR/"

# Create Applications symlink
ln -s /Applications "$TMP_DIR/Applications"

# Clean dot-underscore files
find "$TMP_DIR" -name "._*" -delete

# Create temporary DMG
TEMP_DMG="$TMP_DIR/temp.dmg"
echo "Creating temporary DMG..."
hdiutil create -volname "$DMG_MOUNT_NAME" -srcfolder "$TMP_DIR" -ov -format UDRW "$TEMP_DMG"

# Mount the temporary DMG
echo "Mounting DMG for customization..."
MOUNT_POINT=$(hdiutil attach -readwrite -noverify -noautoopen "$TEMP_DMG" | grep "/Volumes" | awk '{print $3}')

if [ -z "$MOUNT_POINT" ]; then
    echo "Error: Failed to mount DMG"
    exit 1
fi

echo "Mounted at: $MOUNT_POINT"

# Copy background image if it exists
if [ -f "$BACKGROUND_IMG" ]; then
    echo "Adding background image..."
    mkdir -p "$MOUNT_POINT/.background"
    cp "$BACKGROUND_IMG" "$MOUNT_POINT/.background/background.png"
    BACKGROUND_FILE=".background/background.png"
else
    echo "Warning: Background image not found at $BACKGROUND_IMG"
    BACKGROUND_FILE=""
fi

# Apply custom view settings using AppleScript
echo "Applying custom view settings..."

osascript <<EOF
tell application "Finder"
    tell disk "$DMG_MOUNT_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 700, 500}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set text size of viewOptions to 12
        set label position of viewOptions to bottom
        
        -- Set background if available
        if "$BACKGROUND_FILE" is not "" then
            set background picture of viewOptions to file "$BACKGROUND_FILE" of disk "$DMG_MOUNT_NAME"
        else
            set background picture of viewOptions to none
            set background color of viewOptions to {65535, 65535, 65535}
        end if
        
        -- Position icons
        set position of item "$APP_NAME.app" of container window to {150, 150}
        set position of item "Applications" of container window to {450, 150}
        
        -- Set text color to white (only works if background is set)
        -- Note: Text color is limited in Finder's capabilities
        
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

# Wait for Finder to apply changes
sleep 2

echo "Finalizing DMG..."

# Ensure .background is hidden
SetFile -a V "$MOUNT_POINT/.background" 2>/dev/null || true

# Unmount
hdiutil detach "$MOUNT_POINT" -quiet -force
sync

# Convert to read-only compressed DMG
echo "Compressing DMG..."
rm -f "$DMG_NAME"
hdiutil convert "$TEMP_DMG" -format UDZO -o "$DMG_NAME"

# Cleanup
rm -rf "$TMP_DIR"

if [ -f "$DMG_NAME" ]; then
    echo ""
    echo "✓ Custom DMG created successfully!"
    echo "  Location: $DMG_NAME"
    echo "  Size: $(du -h "$DMG_NAME" | awk '{print $1}')"
else
    echo "Error: DMG creation failed"
    exit 1
fi
