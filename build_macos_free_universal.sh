#!/bin/bash

# Universal Binary Build Script for FonixFlow Free Version (macOS)
# Builds for both Apple Silicon (ARM64) and Intel (x86_64)
# Usage: ./build_macos_free_universal.sh

# Exit on error
set -e

APP_NAME="FonixFlow Free"
SPEC_FILE="fonixflow_free.spec"

echo "=========================================="
echo "📦 Building FonixFlow Free Universal Binary (macOS)"
echo "=========================================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

# Check if Python is universal binary
PYTHON_ARCH=$(file $(which python3) | grep -c "universal binary" || echo "0")
if [ "$PYTHON_ARCH" = "0" ]; then
    echo "Warning: Python is not a universal binary"
    echo "Building for current architecture only..."
    ./build_macos_free.sh
    exit 0
fi

echo "✓ Python is a universal binary"

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: ffmpeg not found in PATH. Ensure it's installed/bundled."
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist
rm -rf "$APP_NAME.app"
rm -rf build_arm64 build_x86_64 dist_arm64 dist_x86_64

# ==========================================
# Build for ARM64 (Apple Silicon)
# ==========================================
echo ""
echo "=========================================="
echo "Building for ARM64 (Apple Silicon)..."
echo "=========================================="

arch -arm64 python3 -m PyInstaller --noconfirm --clean "$SPEC_FILE"

# Move ARM64 build to temporary location
mv build build_arm64
mv dist dist_arm64

echo "✓ ARM64 build complete"

# ==========================================
# Build for x86_64 (Intel)
# ==========================================
echo ""
echo "=========================================="
echo "Building for x86_64 (Intel)..."
echo "=========================================="

arch -x86_64 python3 -m PyInstaller --noconfirm --clean "$SPEC_FILE"

# Move x86_64 build to temporary location
mv build build_x86_64
mv dist dist_x86_64

echo "✓ x86_64 build complete"

# ==========================================
# Create Universal Binary
# ==========================================
echo ""
echo "=========================================="
echo "Creating Universal Binary..."
echo "=========================================="

# Create final dist directory
mkdir -p dist

# Copy ARM64 app as base
cp -R "dist_arm64/$APP_NAME.app" "dist/$APP_NAME.app"

# Find and merge all Mach-O binaries
echo "Merging binaries..."

# Main executable
MAIN_EXEC="FonixFlow Free"
if [ -f "dist/$APP_NAME.app/Contents/MacOS/$MAIN_EXEC" ]; then
    echo "  Merging main executable: $MAIN_EXEC"
    lipo -create \
        "dist_arm64/$APP_NAME.app/Contents/MacOS/$MAIN_EXEC" \
        "dist_x86_64/$APP_NAME.app/Contents/MacOS/$MAIN_EXEC" \
        -output "dist/$APP_NAME.app/Contents/MacOS/$MAIN_EXEC"
fi

# Merge all .so and .dylib files
find "dist/$APP_NAME.app" -type f \( -name "*.so" -o -name "*.dylib" \) | while read -r file; do
    # Get relative path
    rel_path="${file#dist/$APP_NAME.app/}"
    
    arm64_file="dist_arm64/$APP_NAME.app/$rel_path"
    x86_64_file="dist_x86_64/$APP_NAME.app/$rel_path"
    
    if [ -f "$arm64_file" ] && [ -f "$x86_64_file" ]; then
        # Check if files are Mach-O binaries
        if file "$arm64_file" | grep -q "Mach-O"; then
            echo "  Merging: $rel_path"
            lipo -create "$arm64_file" "$x86_64_file" -output "$file"
        fi
    fi
done

# Merge Python framework if it exists
if [ -d "dist/$APP_NAME.app/Contents/Frameworks/Python.framework" ]; then
    echo "  Merging Python framework..."
    find "dist/$APP_NAME.app/Contents/Frameworks/Python.framework" -type f -perm +111 | while read -r file; do
        rel_path="${file#dist/$APP_NAME.app/}"
        arm64_file="dist_arm64/$APP_NAME.app/$rel_path"
        x86_64_file="dist_x86_64/$APP_NAME.app/$rel_path"
        
        if [ -f "$arm64_file" ] && [ -f "$x86_64_file" ]; then
            if file "$arm64_file" | grep -q "Mach-O"; then
                lipo -create "$arm64_file" "$x86_64_file" -output "$file" 2>/dev/null || true
            fi
        fi
    done
fi

echo "✓ Universal binary created"

# Verify universal binary
echo ""
echo "Verifying universal binary..."
MAIN_ARCH=$(file "dist/$APP_NAME.app/Contents/MacOS/$MAIN_EXEC")
if echo "$MAIN_ARCH" | grep -q "universal binary"; then
    echo "✓ Main executable is universal binary"
else
    echo "⚠ Warning: Main executable may not be universal"
    echo "$MAIN_ARCH"
fi

# Clean up temporary builds
echo ""
echo "Cleaning up temporary builds..."
rm -rf build_arm64 build_x86_64 dist_arm64 dist_x86_64

# Create DMG
echo ""
echo "Creating Universal DMG package..."

DMG_NAME="FonixFlow_Free_macOS_Universal.dmg"

# Create DMG using a temporary directory
echo "Preparing app for packaging..."
TMP_DIR=$(mktemp -d)
cp -r "dist/$APP_NAME.app" "$TMP_DIR/"

# Create /Applications symlink
ln -s /Applications "$TMP_DIR/Applications"

# Clean dot-underscore files
find "$TMP_DIR" -name "._*" -delete

echo "Generating DMG..."
if [ -f "dist/$DMG_NAME" ]; then
    rm "dist/$DMG_NAME"
fi

hdiutil create -volname "$APP_NAME" -srcfolder "$TMP_DIR" -ov -format UDZO "dist/$DMG_NAME"

# Cleanup
rm -rf "$TMP_DIR"

if [ -f "dist/$DMG_NAME" ]; then
    echo "✓ DMG created: dist/$DMG_NAME"
else
    echo "Error: DMG creation failed!"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ Universal Build successful!"
echo "========================================="
echo ""
echo "Your universal app is located at: dist/$APP_NAME.app"
echo "DMG package: dist/$DMG_NAME"
echo ""
echo "This app will run natively on both:"
echo "  - Apple Silicon (M1/M2/M3/M4) Macs"
echo "  - Intel Macs"
echo ""
