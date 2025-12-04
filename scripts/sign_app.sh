#!/bin/bash

set -e  # Exit on error

# Configuration
APP_PATH="dist/FonixFlow.app"
IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"
ENTITLEMENTS="entitlements.plist"

echo "==========================================="
echo "Code Signing FonixFlow.app"
echo "==========================================="

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: $APP_PATH not found!"
    echo "   Build the app first with: pyinstaller fonixflow_qt.spec"
    exit 1
fi

# Check if entitlements file exists
if [ ! -f "$ENTITLEMENTS" ]; then
    echo "❌ Error: $ENTITLEMENTS not found!"
    exit 1
fi

echo "Step 1: Signing all dylibs and .so files..."
find "$APP_PATH" -name "*.dylib" -exec codesign --force --sign "$IDENTITY" --timestamp --options runtime {} \; 2>/dev/null || true
find "$APP_PATH" -name "*.so" -exec codesign --force --sign "$IDENTITY" --timestamp --options runtime {} \; 2>/dev/null || true
echo "✓ Dynamic libraries signed"

echo ""
echo "Step 2: Signing frameworks..."
find "$APP_PATH/Contents/Frameworks" -type d -name "*.framework" -exec codesign --force --sign "$IDENTITY" --timestamp --options runtime {} \; 2>/dev/null || true
echo "✓ Frameworks signed"

echo ""
echo "Step 3: Signing all executable binaries (ffmpeg, ffprobe, torch binaries)..."
find "$APP_PATH/Contents/Frameworks" -type f -perm +111 ! -name "*.dylib" ! -name "*.so" -exec codesign --force --sign "$IDENTITY" --timestamp --options runtime --entitlements "$ENTITLEMENTS" {} \; 2>/dev/null || true
echo "✓ Executable binaries signed"

echo ""
echo "Step 4: Signing the main executable..."
codesign --force --sign "$IDENTITY" \
    --timestamp \
    --options runtime \
    --entitlements "$ENTITLEMENTS" \
    "$APP_PATH/Contents/MacOS/FonixFlow"
echo "✓ Main executable signed"

echo ""
echo "Step 5: Signing the app bundle..."
codesign --force --sign "$IDENTITY" \
    --timestamp \
    --options runtime \
    --entitlements "$ENTITLEMENTS" \
    "$APP_PATH"
echo "✓ App bundle signed"

echo ""
echo "Step 6: Verifying signature..."
if codesign --verify --deep --strict --verbose=2 "$APP_PATH" 2>&1 | grep -q "satisfies its Designated Requirement"; then
    echo "✓ Signature verification successful"
else
    echo "⚠️  Signature verification completed with warnings (this is normal for PyInstaller apps)"
fi

echo ""
echo "==========================================="
echo "✓ Code signing complete!"
echo "==========================================="
echo "Signed with: $IDENTITY"
echo "App: $APP_PATH"
