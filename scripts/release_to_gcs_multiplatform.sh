#!/bin/bash
#
# Multi-platform release automation for FonixFlow
# Supports: macOS (Intel/ARM), Windows, Linux
#
# Usage: ./scripts/release_to_gcs_multiplatform.sh <version> <platform>
# Example: ./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm

set -e

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <version> <platform>"
    echo ""
    echo "Platforms:"
    echo "  macos-intel   - macOS Intel (x86_64)"
    echo "  macos-arm     - macOS Apple Silicon (arm64)"
    echo "  windows       - Windows"
    echo "  linux         - Linux"
    echo ""
    echo "Example: $0 1.0.1 macos-arm"
    exit 1
fi

VERSION=$1
PLATFORM=$2
APP_NAME="FonixFlow"
GCS_BUCKET="gs://fonixflow-files/updates"
GCS_PUBLIC_URL="https://storage.googleapis.com/fonixflow-files/updates"

# Validate platform
case "$PLATFORM" in
    macos-intel|macos-arm|windows|linux)
        ;;
    *)
        echo "Error: Invalid platform '$PLATFORM'"
        echo "Valid platforms: macos-intel, macos-arm, windows, linux"
        exit 1
        ;;
esac

echo "========================================="
echo "FonixFlow Multi-Platform Release"
echo "Version: ${VERSION}"
echo "Platform: ${PLATFORM}"
echo "========================================="

# Platform-specific settings
case "$PLATFORM" in
    macos-intel|macos-arm)
        APP_PATH="dist/${APP_NAME}.app"
        if [ ! -d "$APP_PATH" ]; then
            echo "Error: ${APP_PATH} not found!"
            exit 1
        fi
        FILE_EXT="zip"
        PACKAGE_CMD="ditto -c -k --sequesterRsrc --keepParent"
        ;;
    windows)
        APP_PATH="dist/${APP_NAME}.exe"
        if [ ! -f "$APP_PATH" ]; then
            echo "Error: ${APP_PATH} not found!"
            exit 1
        fi
        FILE_EXT="zip"
        PACKAGE_CMD="zip -r"
        ;;
    linux)
        APP_PATH="dist/${APP_NAME}"
        if [ ! -f "$APP_PATH" ] && [ ! -d "$APP_PATH" ]; then
            echo "Error: ${APP_PATH} not found!"
            exit 1
        fi
        FILE_EXT="tar.gz"
        PACKAGE_CMD="tar czf"
        ;;
esac

# Platform-specific paths
PLATFORM_DIR="${PLATFORM}"
ZIP_NAME="${APP_NAME}_${VERSION}_${PLATFORM}.${FILE_EXT}"
ZIP_PATH="dist/${ZIP_NAME}"

echo ""
echo "Step 1: Creating ${FILE_EXT} package..."

# Remove old package if exists
rm -f "$ZIP_PATH"

# Create package
cd dist
case "$PLATFORM" in
    macos-intel|macos-arm)
        ditto -c -k --sequesterRsrc --keepParent "${APP_NAME}.app" "${ZIP_NAME}"
        ;;
    windows)
        zip -r "${ZIP_NAME}" "${APP_NAME}.exe"
        ;;
    linux)
        tar czf "${ZIP_NAME}" "${APP_NAME}"
        ;;
esac
cd ..

echo "✓ Created: ${ZIP_PATH}"
FILE_SIZE_MB=$(du -m "$ZIP_PATH" | cut -f1)
echo "  Size: ${FILE_SIZE_MB} MB"

# Generate SHA256 hash
echo ""
echo "Step 2: Generating SHA256 hash..."
HASH=$(shasum -a 256 "$ZIP_PATH" | cut -d' ' -f1)
echo "✓ SHA256: ${HASH}"

# Upload to GCS
echo ""
echo "Step 3: Uploading to Google Cloud Storage..."

if ! command -v gsutil &> /dev/null; then
    echo "Error: gsutil not found!"
    echo "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "  Uploading ${ZIP_NAME}..."
gsutil cp "$ZIP_PATH" "${GCS_BUCKET}/${PLATFORM_DIR}/${ZIP_NAME}"

echo "✓ Uploaded to: ${GCS_PUBLIC_URL}/${PLATFORM_DIR}/${ZIP_NAME}"
echo "  (Note: File is publicly accessible via bucket-level permissions)"

# Create platform-specific manifest
echo ""
echo "Step 4: Creating manifest for ${PLATFORM}..."

RELEASE_DATE=$(date +%Y-%m-%d)
MANIFEST_FILE="dist/manifest_${PLATFORM}.json"

# Platform display names
case "$PLATFORM" in
    macos-intel) PLATFORM_NAME="macOS (Intel)" ;;
    macos-arm) PLATFORM_NAME="macOS (Apple Silicon)" ;;
    windows) PLATFORM_NAME="Windows" ;;
    linux) PLATFORM_NAME="Linux" ;;
esac

cat > "$MANIFEST_FILE" <<EOF
{
  "latest_version": "${VERSION}",
  "platform": "${PLATFORM}",
  "platform_name": "${PLATFORM_NAME}",
  "download_url": "${GCS_PUBLIC_URL}/${PLATFORM_DIR}/${ZIP_NAME}",
  "release_notes": "## FonixFlow ${VERSION} (${PLATFORM_NAME})\\n\\n- Bug fixes and improvements\\n- Platform-specific optimizations\\n- See full changelog at https://fonixflow.com/changelog",
  "force_update": false,
  "file_hash": "${HASH}",
  "minimum_version": "1.0.0",
  "release_date": "${RELEASE_DATE}",
  "file_size_mb": ${FILE_SIZE_MB}
}
EOF

echo "✓ Created manifest:"
cat "$MANIFEST_FILE"

# Upload manifest
echo ""
echo "Step 5: Uploading manifest to GCS..."
gsutil cp "$MANIFEST_FILE" "${GCS_BUCKET}/${PLATFORM_DIR}/manifest.json"

echo "✓ Manifest uploaded (publicly accessible via bucket-level permissions)"

# Verify deployment
echo ""
echo "Step 6: Verifying deployment..."
MANIFEST_URL="${GCS_PUBLIC_URL}/${PLATFORM_DIR}/manifest.json"

if curl -sf "$MANIFEST_URL" > /dev/null; then
    echo "✓ Manifest is accessible at: $MANIFEST_URL"
else
    echo "⚠ Warning: Could not verify manifest URL"
fi

# Done
echo ""
echo "========================================="
echo "✓ Release ${VERSION} for ${PLATFORM_NAME} deployed!"
echo "========================================="
echo ""
echo "Deployment URLs:"
echo "  Manifest: ${GCS_PUBLIC_URL}/${PLATFORM_DIR}/manifest.json"
echo "  Package:  ${GCS_PUBLIC_URL}/${PLATFORM_DIR}/${ZIP_NAME}"
echo ""
echo "Files created locally:"
echo "  - ${ZIP_PATH}"
echo "  - ${MANIFEST_FILE}"
echo ""
echo "GCS files:"
echo "  - ${GCS_BUCKET}/${PLATFORM_DIR}/${ZIP_NAME}"
echo "  - ${GCS_BUCKET}/${PLATFORM_DIR}/manifest.json"
echo ""
