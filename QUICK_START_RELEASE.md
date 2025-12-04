# Quick Start: FonixFlow Release

The fastest way to create a complete release of FonixFlow.

## Prerequisites

1. **Apple Developer Account** (for code signing)
2. **Google Cloud SDK** installed and authenticated
3. **Environment variables set** (optional, or edit scripts directly)

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
export APPLE_ID="your@email.com"
export TEAM_ID="TEAMID"
export APP_PASSWORD="app-specific-password"
```

## One-Command Release

```bash
./scripts/full_release.sh 1.0.1
```

This single command will:
1. ✓ Update version in code
2. ✓ Build the app
3. ✓ Code sign (if configured)
4. ✓ Notarize (if configured)
5. ✓ Create DMG
6. ✓ Upload DMG to `releases/` folder (for first-time downloaders)
7. ✓ Upload ZIP to `updates/` folder (for auto-updates)
8. ✓ Update manifest

## Platform-Specific Release

```bash
# macOS Apple Silicon
./scripts/full_release.sh 1.0.1 macos-arm

# macOS Intel
./scripts/full_release.sh 1.0.1 macos-intel
```

## Skip Steps (Development/Testing)

```bash
# Skip notarization (faster for testing)
./scripts/full_release.sh 1.0.1 macos-arm --skip-notarize

# Skip DMG creation
./scripts/full_release.sh 1.0.1 macos-arm --skip-dmg

# Skip both
./scripts/full_release.sh 1.0.1 macos-arm --skip-notarize --skip-dmg
```

## Manual Steps (If Needed)

If you prefer step-by-step control:

```bash
# 1. Build
./build_macos.sh

# 2. Sign
./scripts/sign_app.sh

# 3. Notarize
./scripts/notarize_app.sh

# 4. Create DMG
./scripts/create_custom_dmg.sh "FonixFlow" "dist/FonixFlow.app" "dist/FonixFlow.dmg"

# 5. Release to GCS
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm
```

## Troubleshooting

**"gsutil: command not found"**
```bash
brew install google-cloud-sdk
gcloud auth login
```

**"No identity found" (code signing)**
```bash
security find-identity -v -p codesigning
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
```

**Notarization fails**
- Check email for detailed error
- Verify APP_PASSWORD is correct
- Ensure app is code signed first

## DMG Scripts

FonixFlow includes multiple DMG creation scripts:

- **`create_clean_dmg.sh`** - Fastest, no background (for testing)
- **`scripts/create_custom_dmg.sh`** - Production DMG with background (recommended)
- **`create_dmg_working.sh`** - Custom layout with fixed window size
- **`create_icns.sh`** - Create .icns icon file

> **See [doc/DMG_SCRIPTS_GUIDE.md](./doc/DMG_SCRIPTS_GUIDE.md) for complete comparison**

## Full Documentation

- **[RELEASE_WORKFLOW.md](./doc/RELEASE_WORKFLOW.md)** - Complete guide with all details
- [BUILD_MACOS.md](./doc/BUILD_MACOS.md) - Build instructions
- [DMG_CREATION_GUIDE.md](./DMG_CREATION_GUIDE.md) - DMG creation details
- [doc/DMG_SCRIPTS_GUIDE.md](./doc/DMG_SCRIPTS_GUIDE.md) - All DMG scripts compared
- [MULTIPLATFORM_RELEASE.md](./MULTIPLATFORM_RELEASE.md) - Multi-platform workflow
