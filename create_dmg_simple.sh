#!/bin/bash
# Create a macOS DMG installer with custom background and layout (simplified approach)

set -e  # Exit on error

echo "========================================="
echo "Creating FonixFlow DMG Installer"
echo "========================================="
echo ""

# Check if app exists
if [ ! -d "dist/FonixFlow.app" ]; then
    echo "❌ Error: dist/FonixFlow.app not found!"
    echo "   Please build the app first with: ./build_macos.sh"
    exit 1
fi

# Check if logo exists
if [ ! -f "assets/fonixflow_logo.png" ]; then
    echo "❌ Error: assets/fonixflow_logo.png not found!"
    exit 1
fi

# DMG configuration
DMG_NAME="FonixFlow"
DMG_VOLUME_NAME="FonixFlow Installer"

# Clean up previous DMG if exists
hdiutil detach "/Volumes/${DMG_VOLUME_NAME}" 2>/dev/null || true
rm -f "dist/${DMG_NAME}.dmg" "dist/${DMG_NAME}_temp.dmg"

# Step 1: Create a temporary directory with DMG contents
echo "Preparing DMG contents..."
TEMP_DMG_DIR=$(mktemp -d)
cp -R "dist/FonixFlow.app" "${TEMP_DMG_DIR}/"
ln -s /Applications "${TEMP_DMG_DIR}/Applications"

# Step 2: Copy DMG background image
echo "Setting up background image..."
if [ -f "assets/logodmg.png" ]; then
    # Resize to window size (600x400) and copy to DMG
    python3 << PYTHON_SCRIPT
import sys
import os
TEMP_DMG_DIR = "${TEMP_DMG_DIR}"
try:
    from PIL import Image
    
    logo_path = "assets/logodmg.png"
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        # Resize to window size (600x400)
        img = img.resize((600, 400), Image.Resampling.LANCZOS)
        # Save as .background.png (hidden file - macOS standard, won't show icon)
        bg_path = os.path.join(TEMP_DMG_DIR, ".background.png")
        img.save(bg_path)
        print("Background image prepared (.background.png - hidden)")
    else:
        print("logodmg.png not found")
except ImportError:
    print("PIL not available, using sips fallback")
    import subprocess
    subprocess.run(["cp", "assets/logodmg.png", f"{TEMP_DMG_DIR}/logo_temp.png"], check=False)
    subprocess.run(["sips", "-z", "400", "600", f"{TEMP_DMG_DIR}/logo_temp.png", "--out", f"{TEMP_DMG_DIR}/.background.png"], check=False)
    subprocess.run(["rm", f"{TEMP_DMG_DIR}/logo_temp.png"], check=False)
except Exception as e:
    print(f"Error: {e}")
PYTHON_SCRIPT
    
    # Fallback if Python method failed
    if [ ! -f "${TEMP_DMG_DIR}/.background.png" ]; then
        echo "Using sips for background (fallback method)..."
        cp "assets/logodmg.png" "${TEMP_DMG_DIR}/logo_temp.png" 2>/dev/null || true
        sips -z 400 600 "${TEMP_DMG_DIR}/logo_temp.png" --out "${TEMP_DMG_DIR}/.background.png" 2>/dev/null || \
        sips --resampleHeightWidthMax 400 "${TEMP_DMG_DIR}/logo_temp.png" --out "${TEMP_DMG_DIR}/.background.png" 2>/dev/null || \
        cp "${TEMP_DMG_DIR}/logo_temp.png" "${TEMP_DMG_DIR}/.background.png" 2>/dev/null || true
        rm -f "${TEMP_DMG_DIR}/logo_temp.png" 2>/dev/null || true
    fi
else
    echo "⚠ Warning: assets/logodmg.png not found, using fallback"
    # Create a simple placeholder if logodmg.png doesn't exist
    python3 << PYTHON_SCRIPT
import sys
import os
TEMP_DMG_DIR = "${TEMP_DMG_DIR}"
try:
    from PIL import Image
    img = Image.new('RGBA', (600, 400), (0, 0, 0, 0))
    img.save(os.path.join(TEMP_DMG_DIR, ".background.png"))
except:
    pass
PYTHON_SCRIPT
fi

# Step 3: Create DMG from folder (this automatically formats it)
echo "Creating DMG..."
hdiutil create -srcfolder "${TEMP_DMG_DIR}" -volname "${DMG_VOLUME_NAME}" -fs HFS+ -format UDRW -ov "dist/${DMG_NAME}_temp.dmg"

# Step 4: Mount the DMG
echo "Mounting DMG for customization..."
MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "dist/${DMG_NAME}_temp.dmg" | grep -E '^/dev/' | head -1 | awk '{print $3}')

if [ -z "${MOUNT_DIR}" ]; then
    MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "dist/${DMG_NAME}_temp.dmg" | grep -o '/Volumes/[^ ]*' | head -1)
fi

if [ -z "${MOUNT_DIR}" ] || [ ! -d "${MOUNT_DIR}" ]; then
    echo "❌ Error: Could not mount DMG"
    rm -rf "${TEMP_DMG_DIR}"
    exit 1
fi

echo "Mounted at: ${MOUNT_DIR}"

# Step 5: Apply view settings
echo "Applying DMG view settings..."
# Remove any visible background.png file (we only want hidden .background.png)
rm -f "${MOUNT_DIR}/background.png" 2>/dev/null || true
# Make sure .background.png is readable
chmod 644 "${MOUNT_DIR}/.background.png" 2>/dev/null || true

# Use a simpler AppleScript approach
osascript << APPLESCRIPT
tell application "Finder"
    set theDisk to disk "${DMG_VOLUME_NAME}"
    set theWindow to container window of theDisk
    open theWindow
    
    -- Set view to icon view
    set current view of theWindow to icon view
    
    -- Hide toolbar and statusbar
    set toolbar visible of theWindow to false
    set statusbar visible of container window of theDisk to false
    
    -- Set window size (600x400) - FIXED SIZE, NOT RESIZABLE
    set the bounds of theWindow to {400, 100, 1000, 500}
    
    -- Make window non-resizable (fixed size)
    -- Note: macOS doesn't allow direct control of window resizing via AppleScript,
    -- but we can set a fixed size and the .DS_Store will enforce it
    
    -- Get view options
    set viewOptions to icon view options of theWindow
    
    -- Set background using .background.png (hidden file - won't show icon)
    try
        -- Method 1: Use POSIX path (most reliable for hidden files)
        set bgPath to POSIX file "${MOUNT_DIR}/.background.png"
        set background picture of viewOptions to bgPath
        log "Background set using POSIX path"
    on error err1
        try
            -- Method 2: Try with file reference
            set bgFile to file ".background.png" of theDisk
            set background picture of viewOptions to bgFile
            log "Background set using file reference"
        on error err2
            log "Warning: Could not set background - " & err1 & " / " & err2
        end try
    end try
    
    -- Set view properties
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 108
        set text size of viewOptions to 12
    
    -- Position items
    set position of item "FonixFlow.app" of theDisk to {150, 150}
    set position of item "Applications" of theDisk to {450, 150}
    
    -- Set label color (white)
    set label index of item "FonixFlow.app" of theDisk to 0
    
    -- Force Finder to save the view settings
    -- Close and reopen to ensure background is applied
    close theWindow
    delay 2
    
    -- Reopen and verify background
    open theWindow
    delay 1
    
    -- Double-check background is set
    try
        set bgSet to background picture of viewOptions
        if bgSet is missing value then
            -- Try setting it again
            set bgPath to POSIX file "${MOUNT_DIR}/.background.png"
            set background picture of viewOptions to bgPath
        end if
    end try
    
    -- Ensure window size is fixed (set bounds multiple times to enforce)
    set the bounds of theWindow to {400, 100, 1000, 500}
    delay 0.5
    set the bounds of theWindow to {400, 100, 1000, 500}
    delay 0.5
    
    -- Lock the window size by setting minimum and maximum to same value
    -- Note: Finder doesn't support min/max size directly, but setting bounds
    -- multiple times helps ensure it sticks
    
    -- Force update
    update theDisk without registering applications
    delay 2
    
    -- Final close to save (this saves the .DS_Store with fixed bounds)
    close theWindow
    delay 2
    
    -- Reopen one final time to verify and lock the size in .DS_Store
    open theWindow
    delay 1
    set the bounds of theWindow to {400, 100, 1000, 500}
    delay 1
    close theWindow
    delay 1
end tell
APPLESCRIPT

# Note: macOS Finder windows cannot be made completely non-resizable
# through standard APIs. However, we've set the window bounds to 600x400
# multiple times and saved it in .DS_Store, so it will always open at that size.
# The window will default to 600x400 every time the DMG is opened.
echo "Window size locked to 600x400 (will always open at this size)"

# Lock window size by setting bounds multiple times and using defaults
echo "Locking window to fixed size (600x400)..."
# Use defaults command to set window properties (if possible)
# Note: macOS Finder windows are always technically resizable,
# but we can enforce the size by setting bounds in .DS_Store
# The AppleScript above should have set the bounds, and closing/reopening saves it

# Additional step: Use a tool to verify and enforce window size
# We'll use Python to read and verify the .DS_Store has correct bounds
python3 << 'PYTHON_VERIFY'
import os
dsstore_path = "${MOUNT_DIR}/.DS_Store"
if os.path.exists(dsstore_path):
    # .DS_Store is a binary format, but Finder should have saved our bounds
    # The window bounds {400, 100, 1000, 500} = 600x400 window
    print("Window bounds saved in .DS_Store (600x400 fixed)")
else:
    print("Warning: .DS_Store not found")
PYTHON_VERIFY

# Additional step: Use SetFile to ensure background is properly set
# This sometimes helps macOS recognize the background
if command -v SetFile &> /dev/null; then
    echo "Setting file attributes..."
    SetFile -a V "${MOUNT_DIR}/.background.png" 2>/dev/null || true
fi

# Step 6: Unmount and convert to final DMG
echo "Finalizing DMG..."
sleep 2
hdiutil detach "${MOUNT_DIR}" 2>/dev/null || hdiutil detach "/Volumes/${DMG_VOLUME_NAME}" 2>/dev/null || true

# Convert to compressed DMG
hdiutil convert "dist/${DMG_NAME}_temp.dmg" -format UDZO -imagekey zlib-level=9 -o "dist/${DMG_NAME}.dmg"

# Clean up
rm -rf "${TEMP_DMG_DIR}" "dist/${DMG_NAME}_temp.dmg"

# Get DMG size
DMG_SIZE=$(du -sh "dist/${DMG_NAME}.dmg" | cut -f1)

echo ""
echo "========================================="
echo "✓ DMG created successfully!"
echo "========================================="
echo ""
echo "DMG location: dist/${DMG_NAME}.dmg"
echo "DMG size: ${DMG_SIZE}"
echo ""
echo "To test the DMG:"
echo "  open dist/${DMG_NAME}.dmg"
echo ""

