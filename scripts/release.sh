#!/bin/bash

set -e  # Exit on error

# Configuration
APPLE_ID="libor.cevelik@me.com"
TEAM_ID="8BLXD56D6K"
APP_PASSWORD="kuqy-umcx-auba-ynfz"
IDENTITY="Developer ID Application: Libor Cevelik (8BLXD56D6K)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if version argument provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Version number required${NC}"
    echo "Usage: ./scripts/release.sh VERSION"
    echo "Example: ./scripts/release.sh 1.0.1"
    exit 1
fi

VERSION=$1
PLATFORM=$(uname -m)
if [ "$PLATFORM" = "arm64" ]; then
    PLATFORM_NAME="macos-arm"
    PLATFORM_DISPLAY="macOS (Apple Silicon)"
else
    PLATFORM_NAME="macos-intel"
    PLATFORM_DISPLAY="macOS (Intel)"
fi

echo ""
echo "=========================================="
echo "  FonixFlow Release Builder v$VERSION"
echo "  Platform: $PLATFORM_DISPLAY"
echo "=========================================="
echo ""

# Step 1: Update version in code
echo -e "${YELLOW}Step 1/10: Updating version number...${NC}"
cat > app/version.py << EOF
# Auto-generated version file
__version__ = "$VERSION"
EOF
echo -e "${GREEN}✓ Version updated to $VERSION${NC}"

# Step 2: Build app
echo ""
echo -e "${YELLOW}Step 2/10: Building app with PyInstaller...${NC}"
pyinstaller fonixflow_qt.spec --clean
echo -e "${GREEN}✓ App built successfully${NC}"

# Step 3: Sign app
echo ""
echo -e "${YELLOW}Step 3/10: Code signing app...${NC}"
./scripts/sign_app.sh
echo -e "${GREEN}✓ App signed${NC}"

# Step 4: Notarize app
echo ""
echo -e "${YELLOW}Step 4/10: Notarizing app (this may take 5-15 minutes)...${NC}"
rm -f dist/FonixFlow_notarization.zip
ditto -c -k --keepParent dist/FonixFlow.app dist/FonixFlow_notarization.zip

SUBMISSION_OUTPUT=$(xcrun notarytool submit dist/FonixFlow_notarization.zip \
    --apple-id "$APPLE_ID" \
    --team-id "$TEAM_ID" \
    --password "$APP_PASSWORD" \
    --wait \
    --output-format json)

if echo "$SUBMISSION_OUTPUT" | grep -q '"status":"Accepted"'; then
    echo -e "${GREEN}✓ App notarization accepted${NC}"

    # Staple app
    xcrun stapler staple dist/FonixFlow.app
    echo -e "${GREEN}✓ Notarization stapled to app${NC}"
else
    echo -e "${RED}❌ Notarization failed!${NC}"
    echo "$SUBMISSION_OUTPUT"
    exit 1
fi

rm -f dist/FonixFlow_notarization.zip

# Step 5: Create DMG
echo ""
echo -e "${YELLOW}Step 5/10: Creating DMG...${NC}"
./create_clean_dmg.sh
echo -e "${GREEN}✓ DMG created${NC}"

# Step 6: Notarize DMG
echo ""
echo -e "${YELLOW}Step 6/10: Notarizing DMG (this may take 5-15 minutes)...${NC}"
DMG_SUBMISSION=$(xcrun notarytool submit dist/FonixFlow.dmg \
    --apple-id "$APPLE_ID" \
    --team-id "$TEAM_ID" \
    --password "$APP_PASSWORD" \
    --wait \
    --output-format json)

if echo "$DMG_SUBMISSION" | grep -q '"status":"Accepted"'; then
    echo -e "${GREEN}✓ DMG notarization accepted${NC}"

    # Staple DMG
    xcrun stapler staple dist/FonixFlow.dmg
    echo -e "${GREEN}✓ Notarization stapled to DMG${NC}"
else
    echo -e "${RED}❌ DMG notarization failed!${NC}"
    echo "$DMG_SUBMISSION"
    exit 1
fi

# Step 7: Create ZIP for updates
echo ""
echo -e "${YELLOW}Step 7/10: Creating update ZIP...${NC}"
cd dist
rm -f FonixFlow_${VERSION}_${PLATFORM_NAME}.zip
ditto -c -k --keepParent FonixFlow.app FonixFlow_${VERSION}_${PLATFORM_NAME}.zip
cd ..
echo -e "${GREEN}✓ Update ZIP created${NC}"

# Step 8: Calculate SHA256
echo ""
echo -e "${YELLOW}Step 8/10: Calculating file hash...${NC}"
FILE_HASH=$(shasum -a 256 dist/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip | cut -d' ' -f1)
FILE_SIZE_MB=$(du -m dist/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip | cut -f1)
echo -e "${GREEN}✓ SHA256: $FILE_HASH${NC}"
echo -e "${GREEN}✓ Size: ${FILE_SIZE_MB}MB${NC}"

# Step 9: Upload to GCS
echo ""
echo -e "${YELLOW}Step 9/10: Uploading to Google Cloud Storage...${NC}"

# Upload ZIP
gsutil cp dist/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip \
    gs://fonixflow-files/updates/${PLATFORM_NAME}/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip

# Upload DMG
gsutil cp dist/FonixFlow.dmg \
    gs://fonixflow-files/releases/FonixFlow_${VERSION}_${PLATFORM_NAME}.dmg

# Make files public
gsutil acl ch -u AllUsers:R gs://fonixflow-files/updates/${PLATFORM_NAME}/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip
gsutil acl ch -u AllUsers:R gs://fonixflow-files/releases/FonixFlow_${VERSION}_${PLATFORM_NAME}.dmg

echo -e "${GREEN}✓ Files uploaded${NC}"

# Step 10: Update manifest
echo ""
echo -e "${YELLOW}Step 10/10: Updating manifest...${NC}"
RELEASE_DATE=$(date +%Y-%m-%d)

cat > dist/manifest_${PLATFORM_NAME}.json << EOF
{
  "latest_version": "$VERSION",
  "platform": "$PLATFORM_NAME",
  "platform_name": "$PLATFORM_DISPLAY",
  "download_url": "https://storage.googleapis.com/fonixflow-files/updates/${PLATFORM_NAME}/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip",
  "release_notes": "## FonixFlow $VERSION ($PLATFORM_DISPLAY)\\n\\n- Bug fixes and improvements\\n- Platform-specific optimizations\\n- See full changelog at https://fonixflow.com/changelog",
  "force_update": false,
  "file_hash": "$FILE_HASH",
  "minimum_version": "$VERSION",
  "release_date": "$RELEASE_DATE",
  "file_size_mb": $FILE_SIZE_MB
}
EOF

# Upload manifest
gsutil cp dist/manifest_${PLATFORM_NAME}.json \
    gs://fonixflow-files/updates/${PLATFORM_NAME}/manifest.json

gsutil acl ch -u AllUsers:R \
    gs://fonixflow-files/updates/${PLATFORM_NAME}/manifest.json

echo -e "${GREEN}✓ Manifest updated${NC}"

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}✓ Release $VERSION Complete!${NC}"
echo "=========================================="
echo ""
echo "📦 Downloads:"
echo "   ZIP: https://storage.googleapis.com/fonixflow-files/updates/${PLATFORM_NAME}/FonixFlow_${VERSION}_${PLATFORM_NAME}.zip"
echo "   DMG: https://storage.googleapis.com/fonixflow-files/releases/FonixFlow_${VERSION}_${PLATFORM_NAME}.dmg"
echo ""
echo "📋 Manifest:"
echo "   https://storage.googleapis.com/fonixflow-files/updates/${PLATFORM_NAME}/manifest.json"
echo ""
echo "🔐 Security:"
echo "   ✓ Code signed with Developer ID"
echo "   ✓ Notarized by Apple"
echo "   ✓ SHA256: $FILE_HASH"
echo ""
echo "📊 Size: ${FILE_SIZE_MB}MB"
echo ""
