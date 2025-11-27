# DMG Creation Guide for FonixFlow

This guide explains how to create a distributable DMG file for the FonixFlow macOS application.

## Prerequisites

1. **Homebrew** - Package manager for macOS
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **create-dmg tool** - Automated DMG creation utility
   ```bash
   brew install create-dmg
   ```

3. **Built application** - FonixFlow.app must be built first
   ```bash
   python3 -m PyInstaller fonixflow_qt.spec --clean --noconfirm
   ```

## Quick Start

### One-Command DMG Creation

From the project root directory:

```bash
cd dist && create-dmg \
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

This creates a professional DMG with:
- Volume name: "FonixFlow Installer"
- Window size: 600×400 pixels
- App icon at position (150, 200)
- Applications symlink at position (450, 200)
- Icon size: 100 pixels

## DMG Configuration Options

### Window Settings

```bash
--volname "NAME"              # Volume name shown in Finder
--window-pos X Y              # Initial window position on screen
--window-size WIDTH HEIGHT    # Window dimensions in pixels
```

### Icon Layout

```bash
--icon-size SIZE              # Icon size in pixels (default: 80)
--icon "FILE" X Y             # Position specific file icon
--app-drop-link X Y           # Position of Applications folder link
--hide-extension "FILE"       # Hide file extension in Finder
```

### Background Image (Optional)

```bash
--background "path/to/image.png"  # Custom background image
```

Image requirements:
- Format: PNG or TIFF
- Recommended size: 600×400 pixels (match window size)
- Will be copied to `.background/` folder in DMG

### Advanced Options

```bash
--no-internet-enable          # Don't add internet-enable flag (faster downloads)
--format FORMAT               # UDZO (compressed), UDBZ (bzip2), UDIF (uncompressed)
--filesystem FORMAT           # HFS+ (default), APFS
--code-sign "IDENTITY"        # Code signing identity from Keychain
```

## Step-by-Step Process

### 1. Build the Application

```bash
# From project root
python3 -m PyInstaller fonixflow_qt.spec --clean --noconfirm
```

This creates: `dist/FonixFlow.app`

### 2. Prepare License Encoding (Optional)

```bash
./tools/prepare_build.sh
```

This encodes the license file for distribution.

### 3. Create the DMG

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

Output: `dist/FonixFlow.dmg`

### 4. Verify the DMG

```bash
# Check file size
ls -lh dist/FonixFlow.dmg

# Calculate checksum
md5 dist/FonixFlow.dmg

# Test mounting
hdiutil attach dist/FonixFlow.dmg
# Verify contents, then eject
hdiutil detach /Volumes/FonixFlow\ Installer
```

## Troubleshooting

### Issue: "Permission denied" when creating DMG

**Solution:** Unmount any existing FonixFlow volumes
```bash
hdiutil detach /Volumes/FonixFlow 2>/dev/null || true
hdiutil detach "/Volumes/FonixFlow Installer" 2>/dev/null || true
```

### Issue: DMG is too large

**Solution 1:** Use better compression
```bash
create-dmg --format UDBZ ...  # Use bzip2 compression
```

**Solution 2:** Remove unnecessary files from .app bundle
```bash
# Check bundle size breakdown
du -sh dist/FonixFlow.app/*
```

### Issue: Background image doesn't appear

**Cause:** Image format or permissions issue

**Solution:**
1. Ensure image is PNG or TIFF format
2. Use absolute path to background image
3. Check image file permissions

### Issue: Icons not positioned correctly

**Solution:** Adjust coordinates in create-dmg command
```bash
--icon "FonixFlow.app" 150 200    # X=150, Y=200
--app-drop-link 450 200           # X=450, Y=200
```

Coordinates are in pixels from top-left corner.

## Using Custom Script

The project includes a custom DMG creation script:

```bash
./scripts/create_custom_dmg.sh 'FonixFlow' 'dist/FonixFlow.app' 'dist/FonixFlow.dmg'
```

With custom background:
```bash
./scripts/create_custom_dmg.sh 'FonixFlow' 'dist/FonixFlow.app' 'dist/FonixFlow.dmg' 'assets/dmg_background.png'
```

## Full Release Build Process

For a complete release build:

```bash
# 1. Build the app
python3 -m PyInstaller fonixflow_qt.spec --clean --noconfirm

# 2. Encode licenses (optional)
./tools/prepare_build.sh

# 3. Create DMG
cd dist && create-dmg \
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

# 4. Calculate checksum for distribution
cd ..
md5 dist/FonixFlow.dmg > dist/FonixFlow.dmg.md5
```

## DMG Distribution Checklist

Before distributing the DMG:

- [ ] App launches correctly from DMG
- [ ] All required files are bundled (ffmpeg, models, etc.)
- [ ] Code signing applied (if distributing outside App Store)
- [ ] DMG mounts correctly on target macOS versions
- [ ] License files are encoded (not plaintext test keys)
- [ ] Update manifest generated (if using auto-update)
- [ ] Checksum calculated and documented
- [ ] Release notes prepared

## Expected Results

A properly created DMG should:
- Size: ~330-350 MB (compressed)
- Format: UDZO (compressed image)
- Window: 600×400 pixels
- Layout: App on left, Applications link on right
- User experience: Drag app to Applications to install

## Common DMG Layouts

### Standard Layout (Current)
```
┌─────────────────────────────────┐
│                                 │
│   [FonixFlow]    →  [Apps]     │
│                                 │
└─────────────────────────────────┘
```

### With Background Image
```
┌─────────────────────────────────┐
│     Custom Background Image     │
│   [FonixFlow]    →  [Apps]     │
│  "Drag to install FonixFlow"    │
└─────────────────────────────────┘
```

## Additional Resources

- **create-dmg documentation:** https://github.com/create-dmg/create-dmg
- **Apple DMG guidelines:** https://developer.apple.com/documentation/
- **Code signing guide:** `codesign --help`

## Notes

- DMG creation requires macOS (cannot be done on Linux/Windows)
- The `--no-internet-enable` flag prevents macOS from setting the "downloaded from internet" quarantine flag
- For App Store distribution, use different packaging (`.pkg` file)
- Consider notarization for macOS Catalina and later: `xcrun notarytool submit`
