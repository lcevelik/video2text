#!/bin/bash
# Script to build a release of FonixFlow with proper versioning

set -e  # Exit on error

# Configuration
VERSION="${1:-1.0.0}"
APP_NAME="FonixFlow"
BUILD_DIR="build"
DIST_DIR="dist"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "================================"
echo "Building FonixFlow Release"
echo "Version: $VERSION"
echo "================================"
echo ""

cd "$PROJECT_ROOT"

# Update version in app/version.py
echo "Updating version to $VERSION..."
python3 << EOF
version_str = "$VERSION"
parts = version_str.split('.')
build_number = int(parts[0]) * 100 + int(parts[1]) * 10 + int(parts[2])

version_content = '''"""
Version information for FonixFlow.

This is the single source of truth for the application version.
Update this file before creating a release.
"""

# Semantic versioning: MAJOR.MINOR.PATCH
__version__ = "$VERSION"
__build__ = "{}"  # Build number (increment with each build)

# Human-readable version string
VERSION_NAME = f"{{__version__}}"
VERSION_WITH_BUILD = f"{{__version__}} (build {{__build__}})"

def get_version():
    """Return the current application version."""
    return __version__

def get_version_string():
    """Return the full version string including build number."""
    return VERSION_WITH_BUILD
'''.format(build_number)

with open('app/version.py', 'w') as f:
    f.write(version_content)

print(f"Version updated to {version_str} (build {build_number})")
EOF

echo ""

# Encode license file before build
echo "Encoding license file..."
./tools/prepare_build.sh

echo ""

# Build the .app bundle
echo "Building .app bundle..."
pyinstaller fonixflow_qt.spec

if [ ! -d "$DIST_DIR/$APP_NAME.app" ]; then
    echo "Error: Build failed - $APP_NAME.app not found"
    exit 1
fi

echo ""

# Create release ZIP
echo "Creating release package..."
cd "$DIST_DIR"
ZIP_NAME="${APP_NAME}-${VERSION}.zip"

if [ -f "$ZIP_NAME" ]; then
    rm "$ZIP_NAME"
fi

zip -r -q "$ZIP_NAME" "${APP_NAME}.app"

echo ""

# Calculate SHA256
echo "Calculating SHA256..."
HASH=$(shasum -a 256 "$ZIP_NAME" | awk '{print $1}')
SIZE=$(ls -lh "$ZIP_NAME" | awk '{print $5}')

echo ""

# Create manifest
echo "Creating update manifest..."
MANIFEST_FILE="${APP_NAME}-${VERSION}-manifest.json"
cat > "$MANIFEST_FILE" << EOF
{
  "latest_version": "$VERSION",
  "download_url": "https://cdn.fonixflow.com/releases/$ZIP_NAME",
  "release_notes": "Update to version $VERSION. See release notes for details.",
  "force_update": false,
  "file_hash": "$HASH",
  "file_size": "$SIZE",
  "minimum_version": "1.0.0",
  "published_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo ""
echo "================================"
echo "Build Complete!"
echo "================================"
echo "Release: $APP_NAME-$VERSION"
echo "Location: $(pwd)/$ZIP_NAME"
echo "Size: $SIZE"
echo "SHA256: $HASH"
echo ""
echo "Manifest file: $MANIFEST_FILE"
echo ""
echo "Next steps:"
echo "1. Test the .app bundle: open $APP_NAME.app"
echo "2. Review the manifest file above"
echo "3. Upload $ZIP_NAME to your CDN at:"
echo "   https://cdn.fonixflow.com/releases/$ZIP_NAME"
echo "4. Update manifest.json on your update server with contents from:"
echo "   $MANIFEST_FILE"
echo "5. Verify the update works with a test installation"
echo ""
