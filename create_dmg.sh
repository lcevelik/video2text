#!/bin/bash
# Create a macOS DMG installer with custom background and layout

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
DMG_SIZE="200m"  # Size in MB (adjust if needed)
WINDOW_SIZE="600x400"
APP_ICON_POS="150,150"
APPLICATIONS_LINK_POS="450,150"

# Clean up previous DMG and temp files if exist
if [ -f "dist/${DMG_NAME}.dmg" ]; then
    echo "Removing previous DMG..."
    rm -f "dist/${DMG_NAME}.dmg"
fi
if [ -f "dist/${DMG_NAME}_temp.dmg" ]; then
    echo "Removing previous temp DMG..."
    hdiutil detach "/Volumes/${DMG_VOLUME_NAME}" 2>/dev/null || true
    rm -f "dist/${DMG_NAME}_temp.dmg"
fi

# Calculate actual size needed
echo "Calculating required DMG size..."
APP_SIZE=$(du -sm "dist/FonixFlow.app" | cut -f1)
DMG_SIZE_MB=$((APP_SIZE + 50))  # Add 50MB overhead
echo "App size: ${APP_SIZE}MB, DMG size: ${DMG_SIZE_MB}MB"

# Create temporary DMG with calculated size
echo "Creating temporary DMG..."
TEMP_DMG="dist/${DMG_NAME}_temp.dmg"
hdiutil create -size ${DMG_SIZE_MB}m -volname "${DMG_VOLUME_NAME}" -fs HFS+ -fsargs "-c c=64,a=16,e=16" "${TEMP_DMG}"

# Mount the DMG as read-write
echo "Mounting DMG..."
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen -mountpoint "/Volumes/${DMG_VOLUME_NAME}" "${TEMP_DMG}" 2>&1)
if [ $? -ne 0 ]; then
    # Try without mountpoint
    MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "${TEMP_DMG}" 2>&1)
fi
MOUNT_DIR=$(echo "${MOUNT_OUTPUT}" | grep -E '^/dev/' | head -1 | awk '{print $3}')
if [ -z "${MOUNT_DIR}" ]; then
    # Try alternative method
    MOUNT_DIR=$(echo "${MOUNT_OUTPUT}" | grep -o '/Volumes/[^ ]*' | head -1)
fi
if [ -z "${MOUNT_DIR}" ] || [ ! -d "${MOUNT_DIR}" ]; then
    echo "❌ Error: Could not mount DMG"
    echo "Mount output: ${MOUNT_OUTPUT}"
    exit 1
fi
echo "Mounted at: ${MOUNT_DIR}"

# Verify write permissions
if [ ! -w "${MOUNT_DIR}" ]; then
    echo "⚠ Warning: Mount point is not writable, trying to remount..."
    hdiutil detach "${MOUNT_DIR}" 2>/dev/null
    sleep 1
    MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "${TEMP_DMG}" 2>&1)
    MOUNT_DIR=$(echo "${MOUNT_OUTPUT}" | grep -o '/Volumes/[^ ]*' | head -1)
    if [ ! -w "${MOUNT_DIR}" ]; then
        echo "❌ Error: Cannot get write access to DMG"
        exit 1
    fi
fi

# Wait for mount to be ready
sleep 3

# Copy app to mounted volume
echo "Setting up DMG contents..."
# Use ditto for better copying (preserves resources, handles large files better)
ditto "dist/FonixFlow.app" "${MOUNT_DIR}/FonixFlow.app" || {
    echo "⚠ ditto failed, trying cp..."
    cp -R "dist/FonixFlow.app" "${MOUNT_DIR}/"
}

# Create Applications link
ln -s /Applications "${MOUNT_DIR}/Applications"

# Create .DS_Store for custom view settings
echo "Configuring DMG view settings..."

# Create a temporary directory for DMG setup
TEMP_SETUP_DIR=$(mktemp -d)
cd "${TEMP_SETUP_DIR}"

# Create background image with fade effect
echo "Processing background image..."
# Create a faded version of the logo (20% opacity = 0.2 alpha)
python3 << PYTHON_SCRIPT
import sys
import os
sys.path.insert(0, os.path.abspath('../../'))

try:
    from PIL import Image
    import os
    
    # Load the logo
    logo_path = "../../assets/fonixflow_logo.png"
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        
        # Resize to window size (600x400)
        img = img.resize((600, 400), Image.Resampling.LANCZOS)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Apply 20% opacity (0.2 alpha)
        alpha = img.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.2))  # 20% visibility
        img.putalpha(alpha)
        
        # Save faded background
        bg_path = "background.png"
        img.save(bg_path)
        print(f"Created faded background: {bg_path}")
    else:
        print(f"Warning: Logo not found at {logo_path}")
        # Create a simple placeholder
        img = Image.new('RGBA', (600, 400), (0, 0, 0, 0))
        img.save("background.png")
except ImportError:
    print("PIL not available, using sips fallback...")
    # Fallback: use sips to resize (can't fade easily without PIL)
    cp "../../assets/fonixflow_logo.png" "logo_temp.png" 2>/dev/null || true
    sips -z 400 600 "logo_temp.png" --out "background.png" 2>/dev/null || \
    sips --resampleHeightWidthMax 400 "logo_temp.png" --out "background.png" 2>/dev/null || \
    cp "logo_temp.png" "background.png" 2>/dev/null || true
    rm -f "logo_temp.png" 2>/dev/null || true
except Exception as e:
    print(f"Error creating background: {e}")
    # Create placeholder
    try:
        img = Image.new('RGBA', (600, 400), (0, 0, 0, 0))
        img.save("background.png")
    except:
        pass
PYTHON_SCRIPT

# Fallback if Python method failed
if [ ! -f "background.png" ]; then
    echo "Using sips for background (fallback method)..."
    cp "../../assets/fonixflow_logo.png" "logo_temp.png" 2>/dev/null || true
    sips -z 400 600 "logo_temp.png" --out "background.png" 2>/dev/null || \
    sips --resampleHeightWidthMax 400 "logo_temp.png" --out "background.png" 2>/dev/null || \
    cp "logo_temp.png" "background.png" 2>/dev/null || true
    rm -f "logo_temp.png" 2>/dev/null || true
fi

# Copy background to mounted volume
if [ -f "background.png" ]; then
    cp "background.png" "${MOUNT_DIR}/.background.png"
    echo "Background image set"
else
    echo "⚠ Warning: Could not create background image"
fi

# Create AppleScript to set up the DMG view
echo "Applying DMG view settings..."
osascript << APPLESCRIPT
tell application "Finder"
    tell disk "${DMG_VOLUME_NAME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        -- Window size: 600x400, positioned at 400,100
        set the bounds of container window to {400, 100, 1000, 500}
        set viewOptions to the icon view options of container window
        set background picture of viewOptions to file ".background.png"
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set text size of viewOptions to 12
        
        -- Position the app icon at 150, 150
        set position of item "FonixFlow.app" to {150, 150}
        
        -- Position the Applications link at 450, 150
        set position of item "Applications" to {450, 150}
        
        -- Set label color (closest we can get to white text)
        set label index of item "FonixFlow.app" to 0  -- White label
        
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
APPLESCRIPT

# Wait a moment for changes to apply
sleep 2

# Generate .DS_Store file
echo "Generating .DS_Store..."
# Force Finder to write .DS_Store
osascript << 'APPLESCRIPT2'
tell application "Finder"
    tell disk "${DMG_VOLUME_NAME}"
        close
        open
        delay 1
        close
    end tell
end tell
APPLESCRIPT2

cd - > /dev/null

# Unmount the DMG
echo "Unmounting DMG..."
hdiutil detach "${MOUNT_DIR}"

# Convert to final compressed DMG
echo "Creating final compressed DMG..."
hdiutil convert "${TEMP_DMG}" -format UDZO -imagekey zlib-level=9 -o "dist/${DMG_NAME}.dmg"

# Clean up
rm -f "${TEMP_DMG}"
rm -rf "${TEMP_SETUP_DIR}"

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

