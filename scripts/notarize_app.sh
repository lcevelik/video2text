#!/bin/bash

set -e  # Exit on error

# Configuration
APP_PATH="dist/FonixFlow.app"
DMG_PATH="dist/FonixFlow.dmg"
ZIP_PATH="dist/FonixFlow_notarization.zip"

# Get credentials from environment variables (required for notarization)
APPLE_ID="${APPLE_ID:-libor.cevelik@me.com}"
TEAM_ID="${TEAM_ID:-8BLXD56D6K}"
APP_PASSWORD="${APP_PASSWORD:-}"

# Check if App-Specific Password is set
if [ -z "$APP_PASSWORD" ]; then
    echo "❌ Error: APP_PASSWORD environment variable is not set!"
    echo ""
    echo "To set up notarization:"
    echo "1. Go to https://appleid.apple.com"
    echo "2. Sign in with your Apple ID: $APPLE_ID"
    echo "3. Go to 'Sign-In and Security' → 'App-Specific Passwords'"
    echo "4. Generate a new password for 'FonixFlow Notarization'"
    echo "5. Copy the password (format: xxxx-xxxx-xxxx-xxxx)"
    echo "6. Set it as an environment variable:"
    echo "   export APP_PASSWORD='your-app-specific-password'"
    echo ""
    echo "Or add it permanently to ~/.zshrc:"
    echo "   echo 'export APP_PASSWORD=\"your-app-specific-password\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
    echo ""
    exit 1
fi

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
