#!/bin/bash
#
# Release automation script for FonixFlow
# Packages .app, generates hash, uploads to GCS, updates manifest
#
# Usage: ./scripts/release_to_gcs.sh <version>
# Example: ./scripts/release_to_gcs.sh 1.0.1

set -e  # Exit on error

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1"
    exit 1
fi

VERSION=$1
APP_NAME="FonixFlow"
GCS_BUCKET="gs://fonixflow-files/updates"
GCS_PUBLIC_URL="https://storage.googleapis.com/fonixflow-files/updates"

echo "========================================="
echo "FonixFlow Release Process - v${VERSION}"
echo "========================================="

# 1. Check if .app exists
APP_PATH="dist/${APP_NAME}.app"
if [ ! -d "$APP_PATH" ]; then
    echo "Error: ${APP_PATH} not found!"
    echo "Please build the app first using PyInstaller"
    exit 1
fi

echo ""
echo "Step 1: Creating ZIP package..."
ZIP_NAME="${APP_NAME}_${VERSION}.zip"
ZIP_PATH="dist/${ZIP_NAME}"

# Remove old ZIP if exists
rm -f "$ZIP_PATH"

# Create ZIP (using ditto to preserve macOS metadata)
cd dist
ditto -c -k --sequesterRsrc --keepParent "${APP_NAME}.app" "${ZIP_NAME}"
cd ..

echo "✓ Created: ${ZIP_PATH}"
FILE_SIZE_MB=$(du -m "$ZIP_PATH" | cut -f1)
echo "  Size: ${FILE_SIZE_MB} MB"

# 2. Generate SHA256 hash
echo ""
echo "Step 2: Generating SHA256 hash..."
HASH=$(shasum -a 256 "$ZIP_PATH" | cut -d' ' -f1)
echo "✓ SHA256: ${HASH}"

# 3. Upload to GCS
echo ""
echo "Step 3: Uploading to Google Cloud Storage..."

# Check if gsutil is available
if ! command -v gsutil &> /dev/null; then
    echo "Error: gsutil not found!"
    echo "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Upload ZIP
echo "  Uploading ${ZIP_NAME}..."
gsutil cp "$ZIP_PATH" "${GCS_BUCKET}/${ZIP_NAME}"

echo "✓ Uploaded to: ${GCS_PUBLIC_URL}/${ZIP_NAME}"
echo "  (Note: File is publicly accessible via bucket-level permissions)"

# 4. Create/Update manifest.json
echo ""
echo "Step 4: Creating manifest.json..."

RELEASE_DATE=$(date +%Y-%m-%d)
MANIFEST_FILE="dist/manifest.json"

cat > "$MANIFEST_FILE" <<EOF
{
  "latest_version": "${VERSION}",
  "download_url": "${GCS_PUBLIC_URL}/${ZIP_NAME}",
  "release_notes": "## FonixFlow ${VERSION}\\n\\n- Bug fixes and improvements\\n- See full changelog at https://fonixflow.com/changelog",
  "force_update": false,
  "file_hash": "${HASH}",
  "minimum_version": "1.0.0",
  "release_date": "${RELEASE_DATE}",
  "file_size_mb": ${FILE_SIZE_MB}
}
EOF

echo "✓ Created manifest.json:"
cat "$MANIFEST_FILE"

# 5. Upload manifest
echo ""
echo "Step 5: Uploading manifest to GCS..."
gsutil cp "$MANIFEST_FILE" "${GCS_BUCKET}/manifest.json"

echo "✓ Manifest uploaded (publicly accessible via bucket-level permissions)"

# 6. Verify manifest is accessible
echo ""
echo "Step 6: Verifying deployment..."
MANIFEST_URL="${GCS_PUBLIC_URL}/manifest.json"

if curl -sf "$MANIFEST_URL" > /dev/null; then
    echo "✓ Manifest is accessible at: $MANIFEST_URL"
else
    echo "⚠ Warning: Could not verify manifest URL"
fi

# Done!
echo ""
echo "========================================="
echo "✓ Release ${VERSION} deployed successfully!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Test update: Launch app and check for updates"
echo "2. Verify download: ${GCS_PUBLIC_URL}/${ZIP_NAME}"
echo "3. Update release notes in manifest if needed"
echo ""
echo "Files created:"
echo "  - ${ZIP_PATH}"
echo "  - ${MANIFEST_FILE}"
echo ""
echo "GCS files:"
echo "  - ${GCS_BUCKET}/${ZIP_NAME}"
echo "  - ${GCS_BUCKET}/manifest.json"
echo ""
