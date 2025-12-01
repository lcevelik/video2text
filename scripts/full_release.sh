#!/bin/bash
#
# Complete Release Workflow for FonixFlow
# Handles: Build → Sign → Notarize → DMG → GCS Upload
#
# Usage: ./scripts/full_release.sh <version> [platform] [--skip-notarize] [--skip-dmg]
#
# Examples:
#   ./scripts/full_release.sh 1.0.1                    # Auto-detect platform
#   ./scripts/full_release.sh 1.0.1 macos-arm           # Specific platform
#   ./scripts/full_release.sh 1.0.1 macos-arm --skip-notarize  # Skip notarization
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
VERSION=""
PLATFORM=""
SKIP_NOTARIZE=false
SKIP_DMG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-notarize)
            SKIP_NOTARIZE=true
            shift
            ;;
        --skip-dmg)
            SKIP_DMG=true
            shift
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION=$1
            elif [ -z "$PLATFORM" ]; then
                PLATFORM=$1
            fi
            shift
            ;;
    esac
done

# Validate version
if [ -z "$VERSION" ]; then
    echo -e "${RED}❌ Error: Version number required${NC}"
    echo "Usage: $0 <version> [platform] [--skip-notarize] [--skip-dmg]"
    echo ""
    echo "Examples:"
    echo "  $0 1.0.1                    # Auto-detect platform"
    echo "  $0 1.0.1 macos-arm         # Specific platform"
    echo "  $0 1.0.1 macos-arm --skip-notarize  # Skip notarization"
    exit 1
fi

# Auto-detect platform if not specified
if [ -z "$PLATFORM" ]; then
    DETECTED_ARCH=$(uname -m)
    if [ "$DETECTED_ARCH" = "arm64" ]; then
        PLATFORM="macos-arm"
        PLATFORM_DISPLAY="macOS (Apple Silicon)"
    elif [ "$DETECTED_ARCH" = "x86_64" ]; then
        PLATFORM="macos-intel"
        PLATFORM_DISPLAY="macOS (Intel)"
    else
        echo -e "${RED}❌ Error: Unsupported platform: $DETECTED_ARCH${NC}"
        echo "Please specify platform: macos-arm or macos-intel"
        exit 1
    fi
else
    case "$PLATFORM" in
        macos-arm)
            PLATFORM_DISPLAY="macOS (Apple Silicon)"
            ;;
        macos-intel)
            PLATFORM_DISPLAY="macOS (Intel)"
            ;;
        *)
            echo -e "${RED}❌ Error: Invalid platform: $PLATFORM${NC}"
            echo "Valid platforms: macos-arm, macos-intel"
            exit 1
            ;;
    esac
fi

# Configuration from environment or defaults
CODESIGN_IDENTITY="${CODESIGN_IDENTITY:-Developer ID Application: Libor Cevelik (8BLXD56D6K)}"
APPLE_ID="${APPLE_ID:-libor.cevelik@me.com}"
TEAM_ID="${TEAM_ID:-8BLXD56D6K}"
APP_PASSWORD="${APP_PASSWORD:-}"

# Check prerequisites
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  FonixFlow Complete Release Workflow${NC}"
echo -e "${BLUE}  Version: $VERSION${NC}"
echo -e "${BLUE}  Platform: $PLATFORM_DISPLAY${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Check for required tools
echo -e "${YELLOW}Checking prerequisites...${NC}"
MISSING_TOOLS=()

if ! command -v python3 &> /dev/null; then
    MISSING_TOOLS+=("python3")
fi

# Check for pyinstaller (try venv first, then system)
PYINSTALLER_CMD=""
if [ -f ".venv_mac/bin/pyinstaller" ]; then
    PYINSTALLER_CMD=".venv_mac/bin/pyinstaller"
    echo -e "${GREEN}✓ Using PyInstaller from .venv_mac${NC}"
elif [ -f ".venv311/bin/pyinstaller" ]; then
    PYINSTALLER_CMD=".venv311/bin/pyinstaller"
    echo -e "${GREEN}✓ Using PyInstaller from .venv311${NC}"
elif command -v pyinstaller &> /dev/null; then
    PYINSTALLER_CMD="pyinstaller"
    echo -e "${GREEN}✓ Using system PyInstaller${NC}"
else
    MISSING_TOOLS+=("pyinstaller")
fi
if ! command -v gsutil &> /dev/null; then
    MISSING_TOOLS+=("gsutil (Google Cloud SDK)")
fi
if [ "$SKIP_NOTARIZE" = false ] && [ -z "$APP_PASSWORD" ]; then
    echo -e "${YELLOW}⚠ Warning: APP_PASSWORD not set, notarization will be skipped${NC}"
    SKIP_NOTARIZE=true
fi

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required tools:${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        echo "   - $tool"
    done
    echo ""
    echo "Install missing tools and try again."
    exit 1
fi
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Step 1: Update version
echo -e "${YELLOW}[1/8] Updating version to $VERSION...${NC}"
python3 -c "
version_str = '$VERSION'
parts = version_str.split('.')
build_number = int(parts[0]) * 100 + int(parts[1]) * 10 + int(parts[2])

version_content = f'''\"\"\"
Version information for FonixFlow.
\"\"\"
__version__ = \"{version_str}\"
__build__ = \"{build_number}\"

VERSION_NAME = f\"{{__version__}}\"
VERSION_WITH_BUILD = f\"{{__version__}} (build {{__build__}})\"

def get_version():
    return __version__

def get_version_string():
    return VERSION_WITH_BUILD
'''

with open('app/version.py', 'w') as f:
    f.write(version_content)
"
echo -e "${GREEN}✓ Version updated${NC}"

# Step 2: Prepare build
echo ""
echo -e "${YELLOW}[2/8] Preparing build...${NC}"
if [ -f "./tools/prepare_build.sh" ]; then
    ./tools/prepare_build.sh
    echo -e "${GREEN}✓ Build prepared${NC}"
else
    echo -e "${YELLOW}⚠ prepare_build.sh not found, skipping${NC}"
fi

# Step 3: Build app
echo ""
echo -e "${YELLOW}[3/8] Building app (this may take several minutes)...${NC}"
rm -rf build dist

# Use the detected pyinstaller command
if [ -n "$PYINSTALLER_CMD" ]; then
    $PYINSTALLER_CMD fonixflow_qt.spec --clean --noconfirm
else
    # Fallback: try with venv activated
    if [ -f ".venv_mac/bin/activate" ]; then
        source .venv_mac/bin/activate
        pyinstaller fonixflow_qt.spec --clean --noconfirm
    else
        echo -e "${RED}❌ PyInstaller not found!${NC}"
        exit 1
    fi
fi

if [ ! -d "dist/FonixFlow.app" ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ App built successfully${NC}"

# Step 4: Code sign
echo ""
echo -e "${YELLOW}[4/8] Code signing app...${NC}"
if [ -f "./scripts/sign_app.sh" ]; then
    # Temporarily set identity if not already set
    export CODESIGN_IDENTITY
    ./scripts/sign_app.sh
    echo -e "${GREEN}✓ App signed${NC}"
else
    echo -e "${YELLOW}⚠ sign_app.sh not found, skipping code signing${NC}"
fi

# Step 5: Notarize
if [ "$SKIP_NOTARIZE" = false ]; then
    echo ""
    echo -e "${YELLOW}[5/8] Notarizing app (this may take 5-15 minutes)...${NC}"
    if [ -f "./scripts/notarize_app.sh" ]; then
        export APPLE_ID TEAM_ID APP_PASSWORD
        ./scripts/notarize_app.sh
        echo -e "${GREEN}✓ App notarized${NC}"
    else
        echo -e "${YELLOW}⚠ notarize_app.sh not found, skipping notarization${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}[5/8] Skipping notarization (--skip-notarize or no APP_PASSWORD)${NC}"
fi

# Step 6: Create DMG
if [ "$SKIP_DMG" = false ]; then
    echo ""
    echo -e "${YELLOW}[6/8] Creating DMG...${NC}"
    # Try custom DMG first (production quality), fallback to clean DMG (faster)
    if [ -f "./scripts/create_custom_dmg.sh" ] && [ -f "assets/dmg_background.png" ]; then
        ./scripts/create_custom_dmg.sh \
            "FonixFlow" \
            "dist/FonixFlow.app" \
            "dist/FonixFlow_${VERSION}_${PLATFORM}.dmg" \
            "assets/dmg_background.png"
        echo -e "${GREEN}✓ DMG created (with background)${NC}"
    elif [ -f "./create_clean_dmg.sh" ]; then
        ./create_clean_dmg.sh
        # Rename to include version and platform if clean DMG was used
        if [ -f "dist/FonixFlow.dmg" ] && [ ! -f "dist/FonixFlow_${VERSION}_${PLATFORM}.dmg" ]; then
            mv "dist/FonixFlow.dmg" "dist/FonixFlow_${VERSION}_${PLATFORM}.dmg"
        fi
        echo -e "${GREEN}✓ DMG created (clean, no background)${NC}"
    else
        echo -e "${YELLOW}⚠ DMG creation script not found, skipping${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}[6/8] Skipping DMG creation (--skip-dmg)${NC}"
fi

# Step 7: Upload DMG to releases/ folder (for first-time downloaders)
if [ "$SKIP_DMG" = false ]; then
    DMG_FILE="dist/FonixFlow_${VERSION}_${PLATFORM}.dmg"
    # Also check for default DMG name if versioned one doesn't exist
    if [ ! -f "$DMG_FILE" ] && [ -f "dist/FonixFlow.dmg" ]; then
        DMG_FILE="dist/FonixFlow.dmg"
    fi
    
    if [ -f "$DMG_FILE" ]; then
        echo ""
        echo -e "${YELLOW}[7/9] Uploading DMG to releases/ folder...${NC}"
        if command -v gsutil &> /dev/null; then
            GCS_RELEASES_BUCKET="gs://fonixflow-files/releases"
            DMG_NAME=$(basename "$DMG_FILE")
            gsutil cp "$DMG_FILE" "${GCS_RELEASES_BUCKET}/${DMG_NAME}"
            # Make it publicly readable
            gsutil acl ch -u AllUsers:R "${GCS_RELEASES_BUCKET}/${DMG_NAME}" 2>/dev/null || true
            echo -e "${GREEN}✓ DMG uploaded to releases/${DMG_NAME}${NC}"
            echo "   URL: https://storage.googleapis.com/fonixflow-files/releases/${DMG_NAME}"
        else
            echo -e "${YELLOW}⚠ gsutil not found, skipping DMG upload${NC}"
        fi
    else
        echo ""
        echo -e "${YELLOW}[7/9] DMG not found, skipping upload${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}[7/9] Skipping DMG upload (--skip-dmg)${NC}"
fi

# Step 8: Release ZIP to GCS (for auto-updates)
echo ""
echo -e "${YELLOW}[8/9] Releasing ZIP to GCS for auto-updates...${NC}"
if [ -f "./scripts/release_to_gcs_multiplatform.sh" ]; then
    ./scripts/release_to_gcs_multiplatform.sh "$VERSION" "$PLATFORM"
    echo -e "${GREEN}✓ ZIP released to GCS for auto-updates${NC}"
else
    echo -e "${RED}❌ release_to_gcs_multiplatform.sh not found!${NC}"
    exit 1
fi

# Step 9: Summary
echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}✓ Release $VERSION Complete!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""
echo "📦 Files created:"
echo "   App: dist/FonixFlow.app"
if [ "$SKIP_DMG" = false ]; then
    DMG_FILE="dist/FonixFlow_${VERSION}_${PLATFORM}.dmg"
    if [ ! -f "$DMG_FILE" ] && [ -f "dist/FonixFlow.dmg" ]; then
        DMG_FILE="dist/FonixFlow.dmg"
    fi
    if [ -f "$DMG_FILE" ]; then
        echo "   DMG: $DMG_FILE"
    fi
fi
echo "   ZIP: dist/FonixFlow_${VERSION}_${PLATFORM}.zip"
echo ""
echo "🌐 GCS URLs:"
echo ""
echo "   📥 First-time downloads (DMG):"
if [ "$SKIP_DMG" = false ]; then
    DMG_NAME="FonixFlow_${VERSION}_${PLATFORM}.dmg"
    if [ ! -f "dist/${DMG_NAME}" ] && [ -f "dist/FonixFlow.dmg" ]; then
        DMG_NAME="FonixFlow.dmg"
    fi
    echo "      https://storage.googleapis.com/fonixflow-files/releases/${DMG_NAME}"
else
    echo "      (DMG not created)"
fi
echo ""
echo "   🔄 Auto-updates (ZIP):"
echo "      Manifest: https://storage.googleapis.com/fonixflow-files/updates/${PLATFORM}/manifest.json"
echo "      Package:  https://storage.googleapis.com/fonixflow-files/updates/${PLATFORM}/FonixFlow_${VERSION}_${PLATFORM}.zip"
echo ""
echo "📋 Next steps:"
echo "   1. Test the app: open dist/FonixFlow.app"
echo "   2. Test update check in app (wait 3 seconds)"
echo "   3. Share DMG URL for first-time downloads"
echo ""
