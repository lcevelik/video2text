# FonixFlow Release Workflow - Complete Guide

This document consolidates the complete release workflow for FonixFlow, covering build, code signing, DMG creation, and GCS upload.

## Table of Contents

1. [Quick Start (Automated)](#quick-start-automated)
2. [Prerequisites](#prerequisites)
3. [Build Process](#build-process)
4. [Code Signing & Notarization](#code-signing--notarization)
5. [DMG Creation](#dmg-creation)
6. [GCS Upload & Distribution](#gcs-upload--distribution)
7. [Complete Release Checklist](#complete-release-checklist)

---

## Quick Start (Automated)

**One-command release** (recommended):

```bash
./scripts/full_release.sh 1.0.1
```

This script automates the entire workflow:
- ✓ Updates version
- ✓ Builds app
- ✓ Code signs (if configured)
- ✓ Notarizes (if configured)
- ✓ Creates DMG
- ✓ Uploads DMG to `releases/` folder (for first-time downloaders)
- ✓ Uploads ZIP to `updates/` folder (for auto-updates)
- ✓ Updates manifest

**Platform-specific:**
```bash
./scripts/full_release.sh 1.0.1 macos-arm
./scripts/full_release.sh 1.0.1 macos-intel
```

**Skip steps (for testing):**
```bash
./scripts/full_release.sh 1.0.1 --skip-notarize  # Skip notarization
./scripts/full_release.sh 1.0.1 --skip-dmg       # Skip DMG creation
```

> **See [QUICK_START_RELEASE.md](../QUICK_START_RELEASE.md) for more quick start options**

---

## Prerequisites

### Required Software

```bash
# Python and dependencies
brew install python@3.11
pip3 install -r requirements.txt
pip3 install pyinstaller

# Audio/video tools
brew install ffmpeg

# DMG creation
brew install create-dmg

# Google Cloud SDK (for GCS upload)
brew install google-cloud-sdk
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Apple Developer Account

For code signing and notarization:
- **Developer ID Certificate** (for distribution outside App Store)
- **App-Specific Password** (for notarization)
- **Team ID** (from Apple Developer portal)

---

## Build Process

### Quick Build

```bash
# Automated build script
./build_macos.sh
```

This script:
- ✓ Checks prerequisites
- ✓ Creates .icns icon
- ✓ Cleans previous builds
- ✓ Builds .app bundle
- ✓ Creates DMG
- ✓ Optionally code signs (if `CODESIGN_IDENTITY` is set)

### Manual Build

```bash
# 1. Create icon
./create_icns.sh

# 2. Build with PyInstaller
pyinstaller fonixflow_qt.spec

# 3. Verify build
open dist/FonixFlow.app
```

### Platform-Specific Builds

#### macOS Apple Silicon (arm64)
```bash
# On Apple Silicon Mac
pyinstaller fonixflow_qt.spec
# Produces: dist/FonixFlow.app (arm64)
```

#### macOS Intel (x86_64)
```bash
# On Intel Mac or cross-compile on Apple Silicon
arch -x86_64 pyinstaller fonixflow_qt.spec
# Produces: dist/FonixFlow.app (x86_64)
```

---

## Code Signing & Notarization

### Step 1: Get Your Developer ID

```bash
# List available signing identities
security find-identity -v -p codesigning
```

Output example:
```
1) ABC123DEF456 "Developer ID Application: Your Name (TEAMID123)"
```

### Step 2: Set Environment Variable

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID123)"
```

Or add to your shell profile (`~/.zshrc` or `~/.bash_profile`):
```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID123)"
```

### Step 3: Code Sign the App

**Option A: During Build**
```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID123)"
./build_macos.sh
```

**Option B: After Build**
```bash
codesign --deep --force --verify --verbose \
         --sign "$CODESIGN_IDENTITY" \
         --options runtime \
         --entitlements entitlements.plist \
         dist/FonixFlow.app
```

**Verify Signing:**
```bash
codesign --verify --verbose dist/FonixFlow.app
codesign -dv --verbose=4 dist/FonixFlow.app
```

### Step 4: Notarize (Required for Distribution)

Notarization is required for macOS Catalina (10.15) and later.

#### 4a. Create App-Specific Password

1. Go to https://appleid.apple.com
2. Sign in with your Apple ID
3. App-Specific Passwords → Generate
4. Save the password (e.g., `abcd-efgh-ijkl-mnop`)

#### 4b. Create ZIP for Notarization

```bash
ditto -c -k --keepParent dist/FonixFlow.app dist/FonixFlow.zip
```

#### 4c. Submit for Notarization

```bash
xcrun notarytool submit dist/FonixFlow.zip \
    --apple-id "your@email.com" \
    --team-id "TEAMID123" \
    --password "abcd-efgh-ijkl-mnop" \
    --wait
```

**Check Status:**
```bash
xcrun notarytool history \
    --apple-id "your@email.com" \
    --team-id "TEAMID123" \
    --password "abcd-efgh-ijkl-mnop"
```

#### 4d. Staple Notarization Ticket

After notarization succeeds:
```bash
xcrun stapler staple dist/FonixFlow.app
xcrun stapler validate dist/FonixFlow.app
```

### Troubleshooting Code Signing

**"No identity found"**
- Check identity: `security find-identity -v -p codesigning`
- Ensure Developer ID certificate is installed in Keychain

**"Resource fork, Finder information, or similar detritus not allowed"**
- Use `--deep` flag (already included in commands above)
- Or use `ditto` to clean: `ditto dist/FonixFlow.app dist/FonixFlow_clean.app`

**Notarization fails: "The binary uses an SDK older than the one submitted"**
- Update Xcode: `xcode-select --install`
- Rebuild with latest SDK

---

## DMG Creation

FonixFlow includes multiple DMG creation scripts. Choose based on your needs:

### Quick DMG (Fastest, No Background)
```bash
./create_clean_dmg.sh
```
Best for: Testing, quick builds, internal distribution

### Production DMG (With Background) ⭐ Recommended
```bash
./scripts/create_custom_dmg.sh \
  "FonixFlow" \
  "dist/FonixFlow.app" \
  "dist/FonixFlow.dmg" \
  "assets/dmg_background.png"
```
Best for: Production releases, public distribution

### Custom Layout DMG
```bash
./create_dmg_working.sh
```
Best for: Fixed window size, precise positioning

### Using create-dmg Tool
```bash
cd dist
create-dmg \
  --volname "FonixFlow Installer" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "FonixFlow.app" 150 200 \
  --hide-extension "FonixFlow.app" \
  --app-drop-link 450 200 \
  --no-internet-enable \
  "FonixFlow.dmg" \
  "FonixFlow.app"
```

> **📘 See [DMG_SCRIPTS_GUIDE.md](./DMG_SCRIPTS_GUIDE.md) for complete comparison of all DMG scripts**

### DMG Options Explained

| Option | Description |
|--------|-------------|
| `--volname "NAME"` | Volume name shown in Finder |
| `--window-pos X Y` | Initial window position |
| `--window-size W H` | Window dimensions (pixels) |
| `--icon-size SIZE` | Icon size (default: 80) |
| `--icon "FILE" X Y` | Position app icon |
| `--app-drop-link X Y` | Position Applications folder link |
| `--hide-extension` | Hide .app extension |
| `--no-internet-enable` | Prevent quarantine flag |
| `--background IMG` | Custom background image |

### Verify DMG

```bash
# Check file size
ls -lh dist/FonixFlow.dmg

# Calculate checksum
shasum -a 256 dist/FonixFlow.dmg

# Test mounting
hdiutil attach dist/FonixFlow.dmg
# Verify contents, then eject
hdiutil detach /Volumes/FonixFlow\ Installer
```

### Code Sign DMG (Optional)

```bash
codesign --sign "$CODESIGN_IDENTITY" \
         --timestamp \
         dist/FonixFlow.dmg
```

---

## GCS Upload & Distribution

### Platform-Specific Release

FonixFlow uses platform-specific update channels:

```bash
# macOS Apple Silicon
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm

# macOS Intel
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-intel

# Windows
./scripts/release_to_gcs_multiplatform.sh 1.0.1 windows

# Linux
./scripts/release_to_gcs_multiplatform.sh 1.0.1 linux
```

### What the Script Does

1. ✓ Creates ZIP package from .app bundle
2. ✓ Generates SHA256 hash
3. ✓ Uploads to `gs://fonixflow-files/updates/{platform}/`
4. ✓ Creates platform-specific `manifest.json`
5. ✓ Uploads manifest
6. ✓ Verifies deployment

### GCS Bucket Structure

```
gs://fonixflow-files/
├── releases/                          # First-time downloads (DMG files)
│   ├── FonixFlow_1.0.1_macos-arm.dmg
│   ├── FonixFlow_1.0.1_macos-intel.dmg
│   └── ...
└── updates/                           # Auto-updates (ZIP files)
    ├── macos-intel/
    │   ├── manifest.json
    │   └── FonixFlow_1.0.1_macos-intel.zip
    ├── macos-arm/
    │   ├── manifest.json
    │   └── FonixFlow_1.0.1_macos-arm.zip
    ├── windows/
    │   ├── manifest.json
    │   └── FonixFlow_1.0.1_windows.zip
    └── linux/
        ├── manifest.json
        └── FonixFlow_1.0.1_linux.tar.gz
```

**Distribution Strategy:**
- **DMG files** (`releases/`) → For first-time downloaders from website
- **ZIP files** (`updates/`) → For automatic updates within the app

### Public URLs

Each platform has its own manifest URL:
- **macOS Intel**: https://storage.googleapis.com/fonixflow-files/updates/macos-intel/manifest.json
- **macOS ARM**: https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json
- **Windows**: https://storage.googleapis.com/fonixflow-files/updates/windows/manifest.json
- **Linux**: https://storage.googleapis.com/fonixflow-files/updates/linux/manifest.json

### Manual GCS Commands

```bash
# List files
gsutil ls gs://fonixflow-files/updates/macos-arm/

# Upload file
gsutil cp dist/FonixFlow_1.0.1_macos-arm.zip \
          gs://fonixflow-files/updates/macos-arm/

# Make public (if bucket-level permissions not set)
gsutil acl ch -u AllUsers:R \
          gs://fonixflow-files/updates/macos-arm/FonixFlow_1.0.1_macos-arm.zip

# Download manifest
gsutil cp gs://fonixflow-files/updates/macos-arm/manifest.json .

# Delete old version
gsutil rm gs://fonixflow-files/updates/macos-arm/FonixFlow_1.0.0_macos-arm.zip
```

### Verify Deployment

```bash
# Test manifest URL
curl https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json

# Test download URL
curl -I https://storage.googleapis.com/fonixflow-files/updates/macos-arm/FonixFlow_1.0.1_macos-arm.zip
```

---

## Complete Release Checklist

### Pre-Release

- [ ] Update version in `app/version.py`
- [ ] Update `CHANGELOG.md`
- [ ] Test app functionality
- [ ] Verify all dependencies are bundled
- [ ] Check license files (not test keys)

### Build

- [ ] Clean previous builds: `rm -rf build dist`
- [ ] Build app: `./build_macos.sh` or `pyinstaller fonixflow_qt.spec`
- [ ] Test app launches: `open dist/FonixFlow.app`
- [ ] Verify all features work

### Code Signing (Production Only)

- [ ] Set `CODESIGN_IDENTITY` environment variable
- [ ] Code sign app: `codesign --sign ...`
- [ ] Verify signing: `codesign --verify --verbose dist/FonixFlow.app`
- [ ] Create ZIP for notarization: `ditto -c -k ...`
- [ ] Submit for notarization: `xcrun notarytool submit ...`
- [ ] Wait for notarization (check status)
- [ ] Staple ticket: `xcrun stapler staple dist/FonixFlow.app`
- [ ] Validate: `xcrun stapler validate dist/FonixFlow.app`

### DMG Creation

- [ ] Create DMG: `create-dmg ...` or `./scripts/create_custom_dmg.sh ...`
- [ ] Verify DMG mounts correctly
- [ ] Test installation from DMG
- [ ] Calculate checksum: `shasum -a 256 dist/FonixFlow.dmg`
- [ ] (Optional) Code sign DMG

### GCS Upload

- [ ] Authenticate: `gcloud auth login`
- [ ] Set project: `gcloud config set project YOUR_PROJECT_ID`
- [ ] Release to GCS: `./scripts/release_to_gcs_multiplatform.sh VERSION PLATFORM`
- [ ] Verify manifest URL is accessible
- [ ] Verify download URL is accessible
- [ ] Test update check in app (wait 3 seconds after launch)

### Post-Release

- [ ] Update website with new version
- [ ] Announce release (if applicable)
- [ ] Monitor update downloads
- [ ] Check error logs for issues

---

## Troubleshooting

### Build Issues

**"Module not found"**
- Add to `hiddenimports` in `fonixflow_qt.spec`

**"FFmpeg not found"**
- Install: `brew install ffmpeg`
- Verify: `which ffmpeg`
- Update spec file if needed

**App crashes on launch**
- Run from terminal: `./dist/FonixFlow.app/Contents/MacOS/FonixFlow`
- Check logs: `~/.fonixflow/logs/`

### Code Signing Issues

**"No identity found"**
- Install Developer ID certificate in Keychain
- Check: `security find-identity -v -p codesigning`

**Notarization fails**
- Check email for detailed error
- Common: SDK version, missing entitlements, unsigned dependencies

### GCS Upload Issues

**"gsutil: command not found"**
- Install: `brew install google-cloud-sdk`
- Or: https://cloud.google.com/sdk/docs/install

**"AccessDeniedException: 403"**
- Authenticate: `gcloud auth login`
- Verify bucket permissions
- Check project: `gcloud config get-value project`

**Update not showing in app**
- Check 24h throttle: Delete `~/.fonixflow/update_config.json`
- Verify manifest URL is correct
- Check app logs for update errors

---

## Quick Reference

### Complete Release Command Sequence

```bash
# 1. Set version
# Edit app/version.py

# 2. Build
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
./build_macos.sh

# 3. Notarize (if code signed)
ditto -c -k --keepParent dist/FonixFlow.app dist/FonixFlow.zip
xcrun notarytool submit dist/FonixFlow.zip \
    --apple-id "your@email.com" \
    --team-id "TEAMID" \
    --password "app-specific-password" \
    --wait
xcrun stapler staple dist/FonixFlow.app

# 4. Create DMG
cd dist
create-dmg --volname "FonixFlow Installer" \
           --window-pos 200 120 \
           --window-size 600 400 \
           --icon-size 100 \
           --icon "FonixFlow.app" 150 200 \
           --hide-extension "FonixFlow.app" \
           --app-drop-link 450 200 \
           --no-internet-enable \
           "FonixFlow.dmg" \
           "FonixFlow.app"
cd ..

# 5. Release to GCS
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-arm
./scripts/release_to_gcs_multiplatform.sh 1.0.1 macos-intel
```

---

## Related Documentation

- [BUILD_MACOS.md](./BUILD_MACOS.md) - Detailed build instructions
- [DMG_CREATION_GUIDE.md](../DMG_CREATION_GUIDE.md) - DMG creation details
- [RELEASE_PROCESS.md](../RELEASE_PROCESS.md) - Single-platform release
- [MULTIPLATFORM_RELEASE.md](../MULTIPLATFORM_RELEASE.md) - Multi-platform release

---

## Notes

- **Code signing is optional** for development but **required** for distribution
- **Notarization is required** for macOS 10.15+ (Catalina and later)
- **DMG is for initial downloads**; auto-updates use ZIP from GCS
- **Platform detection** is automatic in the app
- **24-hour throttle** prevents excessive update checks
