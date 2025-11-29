# FonixFlow Release Scripts

Automated scripts for building, signing, notarizing, and releasing FonixFlow.

## Quick Start

### Production Release (One Command)

```bash
./scripts/release.sh 1.0.1
```

This single command will:
1. ✅ Update version number in code
2. ✅ Build app with PyInstaller
3. ✅ Code sign all binaries
4. ✅ Notarize app with Apple (5-15 min)
5. ✅ Create DMG
6. ✅ Notarize DMG with Apple (5-15 min)
7. ✅ Create update ZIP
8. ✅ Calculate SHA256 hash
9. ✅ Upload to Google Cloud Storage
10. ✅ Update manifest.json

**Total time:** ~15-30 minutes (mostly waiting for Apple notarization)

### Development Workflow

For testing during development (no signing/notarization needed):

```bash
pyinstaller fonixflow_qt.spec
./dist/FonixFlow.app/Contents/MacOS/FonixFlow
```

Or just run from source:
```bash
python fonixflow_qt.py
```

## Individual Scripts

### `release.sh` - Complete Release Automation

**Usage:**
```bash
./scripts/release.sh VERSION
```

**Example:**
```bash
./scripts/release.sh 1.0.2
```

**Requirements:**
- macOS with Xcode Command Line Tools
- Developer ID Application certificate in Keychain
- Google Cloud SDK configured (`gcloud auth login`)
- Apple Developer account credentials configured

**Environment:**
- Apple ID: libor.cevelik@me.com
- Team ID: 8BLXD56D6K
- App-specific password: Embedded in script
- Code signing identity: Developer ID Application: Libor Cevelik (8BLXD56D6K)

---

### `sign_app.sh` - Code Signing Only

Signs the app for distribution (required before notarization).

**Usage:**
```bash
./scripts/sign_app.sh
```

**What it signs:**
- All .dylib files (dynamic libraries)
- All .so files (Python extensions)
- All .framework bundles
- All executable binaries (ffmpeg, ffprobe, torch binaries)
- Main executable
- App bundle

**Requirements:**
- `dist/FonixFlow.app` must exist (run PyInstaller first)
- `entitlements.plist` must exist in project root
- Developer ID certificate in Keychain

---

### `notarize_app.sh` - App Notarization Only

Notarizes the signed app with Apple.

**Usage:**
```bash
./scripts/notarize_app.sh
```

**Process:**
1. Creates ZIP for notarization
2. Uploads to Apple (5-15 minutes)
3. Waits for approval
4. Staples notarization ticket to app
5. Creates DMG (attempts stapling, may fail - normal)

**Requirements:**
- App must be signed first (`./scripts/sign_app.sh`)
- Apple Developer account
- App-specific password

**Note:** DMG stapling may fail in this script. Use `release.sh` for complete DMG notarization.

---

## Release Workflow Comparison

### Option 1: Automated (Recommended)
```bash
./scripts/release.sh 1.0.2
# ☕ Get coffee, wait 15-30 minutes
# Done! ✅
```

### Option 2: Manual (Not Recommended)
```bash
# 1. Update version
vim app/version.py

# 2. Build
pyinstaller fonixflow_qt.spec --clean

# 3. Sign
./scripts/sign_app.sh

# 4. Notarize app
./scripts/notarize_app.sh

# 5. Notarize DMG
xcrun notarytool submit dist/FonixFlow.dmg --apple-id ... --wait
xcrun stapler staple dist/FonixFlow.dmg

# 6. Create ZIP
cd dist && ditto -c -k --keepParent FonixFlow.app FonixFlow_1.0.2_macos-arm.zip && cd ..

# 7. Calculate hash
shasum -a 256 dist/FonixFlow_1.0.2_macos-arm.zip

# 8. Upload to GCS
gsutil cp dist/FonixFlow_1.0.2_macos-arm.zip gs://fonixflow-files/...
gsutil cp dist/FonixFlow.dmg gs://fonixflow-files/...

# 9. Update manifest
vim dist/manifest_macos-arm.json
gsutil cp dist/manifest_macos-arm.json gs://fonixflow-files/...

# 😫 Exhausting!
```

## Troubleshooting

### Code Signing Fails

**Error:** `errSecInternalComponent`
- **Cause:** Keychain locked or certificate not found
- **Fix:** Open Keychain Access, unlock login keychain, verify certificate exists

### Notarization Rejected

**Error:** `status: Invalid`
- **Cause:** Unsigned binaries detected
- **Fix:** Check notarization log (`xcrun notarytool log SUBMISSION_ID`), ensure all executables signed

### Upload Fails

**Error:** `gsutil: command not found`
- **Cause:** Google Cloud SDK not installed
- **Fix:** Install with `brew install google-cloud-sdk` and run `gcloud auth login`

### DMG Stapling Fails

**Error:** `The staple and validate action failed! Error 65.`
- **Cause:** This is normal in `notarize_app.sh` - DMG wasn't part of original notarization
- **Fix:** Use `release.sh` which notarizes DMG separately, or manually notarize DMG

## Version Management

Version is stored in `app/version.py`:

```python
__version__ = "1.0.0"
```

The `release.sh` script automatically updates this file with the version you provide.

## File Locations

**Build artifacts:**
- `dist/FonixFlow.app` - Signed and notarized app
- `dist/FonixFlow.dmg` - Signed and notarized DMG
- `dist/FonixFlow_VERSION_PLATFORM.zip` - Update package
- `dist/manifest_PLATFORM.json` - Update manifest

**Google Cloud Storage:**
- `gs://fonixflow-files/updates/macos-arm/FonixFlow_VERSION_macos-arm.zip` - Update ZIP
- `gs://fonixflow-files/updates/macos-arm/manifest.json` - Update manifest
- `gs://fonixflow-files/releases/FonixFlow_VERSION_macos-arm.dmg` - DMG for download

**Public URLs:**
- `https://storage.googleapis.com/fonixflow-files/updates/macos-arm/FonixFlow_VERSION_macos-arm.zip`
- `https://storage.googleapis.com/fonixflow-files/updates/macos-arm/manifest.json`
- `https://storage.googleapis.com/fonixflow-files/releases/FonixFlow_VERSION_macos-arm.dmg`

## Security

All releases are:
- ✅ Code signed with Developer ID certificate
- ✅ Notarized by Apple
- ✅ SHA256 verified
- ✅ Timestamped
- ✅ Hardened runtime enabled

## Tips

1. **Use `release.sh` for all production releases** - it's tested and complete
2. **Test locally first** - build with PyInstaller and test before releasing
3. **Wait for notarization** - don't interrupt the process (takes 5-15 min per submission)
4. **Keep credentials secure** - the app-specific password in scripts is low-privilege
5. **Version naming** - use semantic versioning (MAJOR.MINOR.PATCH)

## Examples

**Patch release:**
```bash
./scripts/release.sh 1.0.1
```

**Minor release:**
```bash
./scripts/release.sh 1.1.0
```

**Major release:**
```bash
./scripts/release.sh 2.0.0
```

---

**For questions or issues, check the main project documentation or contact the development team.**
