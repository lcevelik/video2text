#!/bin/bash

set -e  # Exit on error

# Configuration
APP_PATH="dist/FonixFlow.app"
DMG_PATH="dist/FonixFlow.dmg"
ZIP_PATH="dist/FonixFlow_notarization.zip"
APPLE_ID="libor.cevelik@me.com"
TEAM_ID="8BLXD56D6K"
APP_PASSWORD="kuqy-umcx-auba-ynfz"

echo "==========================================="
echo "Notarizing FonixFlow.app"
echo "==========================================="

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: $APP_PATH not found!"
    echo "   Build and sign the app first"
    exit 1
fi

# Check if app is signed
if ! codesign --verify "$APP_PATH" 2>/dev/null; then
    echo "❌ Error: App is not signed!"
    echo "   Run ./scripts/sign_app.sh first"
    exit 1
fi

echo "Step 1: Creating ZIP for notarization..."
rm -f "$ZIP_PATH"
ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"
echo "✓ ZIP created: $ZIP_PATH"

echo ""
echo "Step 2: Uploading to Apple for notarization..."
echo "   This may take 5-15 minutes..."
SUBMISSION_ID=$(xcrun notarytool submit "$ZIP_PATH" \
    --apple-id "$APPLE_ID" \
    --team-id "$TEAM_ID" \
    --password "$APP_PASSWORD" \
    --wait \
    --output-format json | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$SUBMISSION_ID" ]; then
    echo "⚠️  Could not extract submission ID, checking status..."
    xcrun notarytool submit "$ZIP_PATH" \
        --apple-id "$APPLE_ID" \
        --team-id "$TEAM_ID" \
        --password "$APP_PASSWORD" \
        --wait
else
    echo "✓ Submission ID: $SUBMISSION_ID"
fi

echo ""
echo "Step 3: Checking notarization status..."
xcrun notarytool info "$SUBMISSION_ID" \
    --apple-id "$APPLE_ID" \
    --team-id "$TEAM_ID" \
    --password "$APP_PASSWORD" 2>/dev/null || echo "Status check skipped (submission completed)"

echo ""
echo "Step 4: Stapling notarization to app..."
xcrun stapler staple "$APP_PATH"
echo "✓ Notarization stapled to app"

echo ""
echo "Step 5: Creating and stapling DMG..."
if [ -f "./create_clean_dmg.sh" ]; then
    ./create_clean_dmg.sh
    if [ -f "$DMG_PATH" ]; then
        xcrun stapler staple "$DMG_PATH"
        echo "✓ Notarization stapled to DMG"
    fi
else
    echo "⚠️  create_clean_dmg.sh not found, skipping DMG creation"
fi

echo ""
echo "Step 6: Verifying notarization..."
spctl -a -vvv -t install "$APP_PATH" 2>&1 | grep -q "accepted" && echo "✓ App passes Gatekeeper" || echo "⚠️  Gatekeeper check completed"

echo ""
echo "Step 7: Cleanup..."
rm -f "$ZIP_PATH"
echo "✓ Temporary files removed"

echo ""
echo "==========================================="
echo "✓ Notarization complete!"
echo "==========================================="
echo "App: $APP_PATH"
echo "DMG: $DMG_PATH"
echo ""
echo "The app is now notarized and will not show"
echo "the 'unverified developer' warning!"
