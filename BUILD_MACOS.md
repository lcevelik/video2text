# Building FonixFlow for macOS

This guide explains how to build FonixFlow as a standalone macOS application bundle (.app) using the provided `.spec` file.

## Prerequisites

### Required Software

1. **macOS 12.3+** (Monterey or later) - Required for ScreenCaptureKit support
2. **Python 3.9+** - Install via Homebrew: `brew install python@3.11`
3. **ffmpeg** - Install via Homebrew: `brew install ffmpeg`
4. **PyInstaller** - Install via pip: `pip3 install pyinstaller`

### Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

For full macOS integration with native system audio capture, also install PyObjC frameworks:

```bash
pip3 install pyobjc-framework-ScreenCaptureKit
pip3 install pyobjc-framework-AVFoundation
pip3 install pyobjc-framework-Cocoa
```

## Quick Build

The easiest way to build is using the provided build script:

```bash
./build_macos.sh
```

This script will:
- Check all prerequisites
- Create the .icns icon file automatically
- Clean previous builds
- Build the .app bundle
- Show instructions for installation and code signing

## Manual Build

If you prefer to build manually:

### 1. Create the Icon File

Convert the PNG icon to macOS .icns format:

```bash
./create_icns.sh
```

Or manually create it:

```bash
mkdir FonixFlow.iconset
sips -z 16 16     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_16x16.png
sips -z 32 32     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_16x16@2x.png
sips -z 32 32     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_32x32.png
sips -z 64 64     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_32x32@2x.png
sips -z 128 128   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_128x128.png
sips -z 256 256   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_128x128@2x.png
sips -z 256 256   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_256x256.png
sips -z 512 512   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_256x256@2x.png
sips -z 512 512   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_512x512.png
sips -z 1024 1024 assets/fonixflow_icon.png --out FonixFlow.iconset/icon_512x512@2x.png
iconutil -c icns FonixFlow.iconset -o assets/fonixflow_icon.icns
rm -rf FonixFlow.iconset
```

### 2. Build with PyInstaller

```bash
pyinstaller fonixflow_qt.spec
```

The build process will:
- Analyze dependencies from `app/fonixflow_qt.py`
- Bundle all Python packages and native libraries
- Include ffmpeg binary (auto-detected from Homebrew paths)
- Package all assets (icons, translations, Whisper model files)
- Create Info.plist with proper permissions
- Apply entitlements for microphone and screen recording

### 3. Install the Application

```bash
cp -r dist/FonixFlow.app /Applications/
```

Or run directly:

```bash
open dist/FonixFlow.app
```

## Understanding the .spec File

The `fonixflow_qt.spec` file is specifically configured for macOS with these features:

### FFmpeg Detection

The spec file automatically detects ffmpeg from multiple locations:
- `/opt/homebrew/bin/ffmpeg` (Apple Silicon - M1/M2)
- `/usr/local/bin/ffmpeg` (Intel Mac)
- `/opt/local/bin/ffmpeg` (MacPorts)

### Hidden Imports

Comprehensive list of all required modules:
- **Core**: Python standard library modules
- **Scientific**: NumPy, SciPy for audio processing
- **Audio**: sounddevice, soundfile, pydub, librosa
- **ML**: PyTorch, Whisper, tiktoken
- **GUI**: PySide6/Qt with SVG support
- **macOS**: PyObjC frameworks (Foundation, Cocoa, AVFoundation, ScreenCaptureKit)
- **App Modules**: All gui, transcription, and app packages

### Data Files

Includes all necessary assets:
- Whisper model tokenizer files (mel_filters.npz, tiktoken files)
- Application icons (PNG, ICO, ICNS)
- SVG icons for UI elements
- Translation files (i18n folder)
- Python source files for dynamic imports

### Entitlements

References `entitlements.plist` which grants:
- `com.apple.security.device.audio-input` - Microphone access
- `com.apple.security.cs.allow-jit` - Required for PyTorch
- `com.apple.security.cs.allow-unsigned-executable-memory` - Required for NumPy
- `com.apple.security.cs.disable-library-validation` - For bundled libraries

### Info.plist Configuration

The BUNDLE section creates a proper macOS app with:
- **Bundle Identifier**: `com.fonixflow.qt`
- **Minimum macOS**: 12.3 (Monterey) for ScreenCaptureKit
- **Permissions**: User-facing descriptions for microphone and screen recording
- **Document Types**: Supports audio/video file drag & drop
- **Dark Mode**: Full support (NSRequiresAquaSystemAppearance: False)
- **High Resolution**: Retina display support

## Code Signing (Optional)

For distribution outside the App Store, you need to code sign with an Apple Developer ID:

### 1. Get Your Developer ID

```bash
security find-identity -v -p codesigning
```

### 2. Sign the Application

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
codesign --deep --force --verify --verbose \
         --sign "$CODESIGN_IDENTITY" \
         --options runtime \
         --entitlements entitlements.plist \
         dist/FonixFlow.app
```

Or set the environment variable before running the build script:

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
./build_macos.sh
```

### 3. Notarize (For Distribution)

For distribution, you also need to notarize with Apple:

```bash
# Create a zip for notarization
ditto -c -k --keepParent dist/FonixFlow.app dist/FonixFlow.zip

# Submit for notarization
xcrun notarytool submit dist/FonixFlow.zip \
    --apple-id "your@email.com" \
    --team-id "TEAMID" \
    --password "app-specific-password"

# Wait for notarization to complete, then staple
xcrun stapler staple dist/FonixFlow.app
```

## Creating a DMG Installer

To create a distributable DMG file:

```bash
hdiutil create -volname FonixFlow \
               -srcfolder dist/FonixFlow.app \
               -ov -format UDZO \
               dist/FonixFlow.dmg
```

For a fancier DMG with custom background and layout, use `create-dmg`:

```bash
brew install create-dmg

create-dmg \
  --volname "FonixFlow Installer" \
  --volicon "assets/fonixflow_icon.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "FonixFlow.app" 200 190 \
  --hide-extension "FonixFlow.app" \
  --app-drop-link 600 185 \
  "dist/FonixFlow.dmg" \
  "dist/FonixFlow.app"
```

## Troubleshooting

### Build Fails with Missing Module

If PyInstaller can't find a module, add it to the `hiddenimports` list in `fonixflow_qt.spec`:

```python
hiddenimports=[
    # ... existing imports ...
    'your_missing_module',
]
```

### App Crashes on Launch

1. Run from Terminal to see error messages:
   ```bash
   ./dist/FonixFlow.app/Contents/MacOS/FonixFlow
   ```

2. Check if all dependencies are included:
   ```bash
   pyinstaller --log-level=DEBUG fonixflow_qt.spec
   ```

### FFmpeg Not Found

The spec file should auto-detect ffmpeg, but if it doesn't:

1. Install ffmpeg: `brew install ffmpeg`
2. Find the path: `which ffmpeg`
3. Update `fonixflow_qt.spec` if needed

### Permissions Denied

macOS requires explicit permissions for:
- **Microphone**: Settings → Privacy & Security → Microphone
- **Screen Recording**: Settings → Privacy & Security → Screen Recording

The app will prompt for these on first use.

### PyObjC Frameworks Not Loading

If native macOS audio capture isn't working:

```bash
pip3 install --force-reinstall \
    pyobjc-framework-ScreenCaptureKit \
    pyobjc-framework-AVFoundation \
    pyobjc-framework-Cocoa
```

## Architecture Support

The spec file builds for the current architecture:
- **Apple Silicon (M1/M2)**: arm64
- **Intel Mac**: x86_64

For a universal binary (both architectures), you need to build on both platforms and use `lipo`:

```bash
# On Intel Mac
pyinstaller fonixflow_qt.spec
mv dist/FonixFlow.app dist/FonixFlow-x86_64.app

# On Apple Silicon
pyinstaller fonixflow_qt.spec
mv dist/FonixFlow.app dist/FonixFlow-arm64.app

# Combine (requires tools from both platforms)
# This is complex - typically done via CI/CD
```

## File Structure

After building, the app structure is:

```
FonixFlow.app/
├── Contents/
│   ├── Info.plist              # App metadata and permissions
│   ├── MacOS/
│   │   └── FonixFlow           # Main executable
│   ├── Resources/
│   │   ├── assets/             # Icons, images
│   │   ├── i18n/               # Translations
│   │   ├── gui/                # GUI modules
│   │   ├── whisper/            # Whisper model files
│   │   └── fonixflow_icon.icns # App icon
│   └── Frameworks/
│       ├── ffmpeg              # Bundled ffmpeg binary
│       └── *.dylib             # Python and dependencies
```

## Further Reading

- [PyInstaller macOS Documentation](https://pyinstaller.org/en/stable/operating-mode.html#mac-os-x-specific-options)
- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [macOS App Permissions](https://developer.apple.com/documentation/bundleresources/information_property_list/protected_resources)
