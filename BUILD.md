# FonixFlow Build Guide

Complete guide for building and packaging FonixFlow on macOS and Windows.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [macOS Build Instructions](#macos-build-instructions)
- [Windows Build Instructions](#windows-build-instructions)
- [Build Outputs](#build-outputs)
- [FFmpeg Requirements](#ffmpeg-requirements)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### All Platforms

1. **Python 3.9 or later** (Python 3.11 recommended)
   - Download from [python.org](https://www.python.org/downloads/)

2. **FFmpeg** (required for audio/video processing)
   - See [FFmpeg Requirements](#ffmpeg-requirements) for installation instructions

3. **Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

### macOS Only

- **macOS 12.3 or later** (for ScreenCaptureKit support)
- **Xcode Command Line Tools**
  ```bash
  xcode-select --install
  ```

### Windows Only

- **Windows 10/11** (64-bit)
- **Microsoft Visual C++ Redistributable** (usually pre-installed)

---

## macOS Build Instructions

### Quick Start

```bash
chmod +x build_macos.sh
./build_macos.sh
```

### What It Does

1. ✅ Checks for Python, ffmpeg, and PyInstaller
2. 🎨 Creates `.icns` icon (if needed)
3. 🧹 Cleans previous builds
4. 📦 Builds `FonixFlow.app` bundle using PyInstaller
5. 🎁 Creates custom DMG installer with:
   - Drag-and-drop installation UI
   - Custom background image
   - Applications folder shortcut
   - Icon positioning

### Build Outputs

- **App Bundle:** `dist/FonixFlow.app`
  - Standalone macOS application
  - Contains all dependencies including ffmpeg
  - Can be copied to `/Applications/`

- **DMG Installer:** `dist/FonixFlow_macOS_Universal.dmg`
  - Professional installer package
  - Users drag app to Applications folder
  - Ready for distribution

### Optional: Code Signing

To sign the app with your Apple Developer ID:

```bash
export CODESIGN_IDENTITY="Developer ID Application: Your Name (TEAMID)"
./build_macos.sh
```

### Manual Build

If you need to build manually:

```bash
pyinstaller fonixflow_qt.spec
```

---

## Windows Build Instructions

### Quick Start

```cmd
build_windows.bat
```

### What It Does

1. ✅ Checks for Python, ffmpeg, and PyInstaller
2. 🧹 Cleans previous builds
3. 📦 Builds single-file executable using PyInstaller
4. ✨ Creates `FonixFlow.exe` (all-in-one, no installer needed)

### Build Outputs

- **Single-File Executable:** `dist/FonixFlow.exe`
  - Standalone Windows executable (~150-200 MB)
  - Contains all dependencies including ffmpeg
  - No installation required - just run it!
  - First launch takes 30-60 seconds (unpacking)
  - Subsequent launches are faster (~5-10 seconds)

### Distribution

Simply share the `dist/FonixFlow.exe` file with users. No installer needed!

**Note:** Windows Defender may scan the file on first run. This is normal for unsigned executables.

### Manual Build

If you need to build manually:

```cmd
pyinstaller fonixflow_qt_windows.spec
```

---

## Build Outputs

### macOS

```
dist/
├── FonixFlow.app/                    # Standalone app bundle
│   ├── Contents/
│   │   ├── MacOS/
│   │   │   ├── FonixFlow            # Main executable
│   │   │   ├── ffmpeg               # Bundled ffmpeg
│   │   │   └── ffprobe              # Bundled ffprobe
│   │   ├── Resources/               # Assets, translations, icons
│   │   └── Info.plist               # App metadata
│   └── ...
└── FonixFlow_macOS_Universal.dmg     # Installer (drag-and-drop)
```

### Windows

```
dist/
└── FonixFlow.exe                     # Single-file executable (~150-200 MB)
                                      # Contains: Python, Qt, PyTorch, Whisper, FFmpeg
```

---

## FFmpeg Requirements

FFmpeg must be installed on your build machine. The build process will automatically bundle it into the application.

### macOS Installation

**Option 1: Homebrew (Recommended)**
```bash
brew install ffmpeg
```

**Option 2: MacPorts**
```bash
sudo port install ffmpeg
```

The build script checks these locations automatically:
- `/opt/homebrew/bin/ffmpeg` (Apple Silicon)
- `/usr/local/bin/ffmpeg` (Intel Mac)
- `/opt/local/bin/ffmpeg` (MacPorts)
- System PATH

### Windows Installation

**Option 1: Chocolatey (Recommended)**
```cmd
choco install ffmpeg
```

**Option 2: Manual Installation**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH

The build script checks these locations automatically:
- System PATH
- `C:\ffmpeg\bin\ffmpeg.exe`
- Chocolatey installation path
- Program Files

### Verifying FFmpeg

```bash
# macOS/Linux
ffmpeg -version

# Windows
ffmpeg.exe -version
```

---

## Troubleshooting

### Common Issues

#### ❌ "ffmpeg not found"

**Cause:** FFmpeg is not installed or not in PATH.

**Solution:**
- macOS: `brew install ffmpeg`
- Windows: `choco install ffmpeg` or add to PATH manually
- Verify with: `ffmpeg -version`

#### ❌ "PyInstaller not found"

**Solution:**
```bash
pip install pyinstaller
```

#### ❌ Build fails with "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

#### ❌ Windows: "UPX is not available"

**Not a problem!** UPX is intentionally disabled to avoid antivirus false positives.

#### ❌ macOS: DMG creation fails

**Cause:** Missing scripts or Finder permissions.

**Solution:**
- Ensure `scripts/create_custom_dmg.sh` exists
- Grant Full Disk Access to Terminal in System Preferences
- Run script will create a basic DMG as fallback

#### ❌ Windows: Executable is flagged by antivirus

**Cause:** Unsigned executables are often flagged.

**Solutions:**
- Add exception to antivirus
- Code sign the executable (requires certificate)
- Build with different Python version (sometimes helps)

#### ❌ App crashes on startup

**Debugging:**

**macOS:**
```bash
# Run from terminal to see errors
./dist/FonixFlow.app/Contents/MacOS/FonixFlow
```

**Windows:**
```cmd
# Run from command prompt to see errors
dist\FonixFlow.exe
```

Common causes:
- Missing dependencies: Reinstall with `pip install -r requirements.txt`
- Corrupt Whisper cache: Delete `~/.cache/whisper`
- Permission issues: Grant microphone/screen recording permissions

#### ❌ Large file size

**Expected Sizes:**
- macOS app bundle: ~800 MB - 1.2 GB
- macOS DMG (compressed): ~400 MB - 600 MB
- Windows EXE: ~150 MB - 250 MB (first launch unpacks to ~800 MB)

**Why so large?**
- PyTorch: ~500 MB
- Qt framework: ~200 MB
- FFmpeg: ~80-120 MB
- Python libraries: ~100 MB

**To reduce size:**
- Whisper models are NOT bundled (downloaded on-demand)
- Full version with bundled models: +150 MB to +2 GB

---

## Advanced Options

### Building Free Version

The free version has usage restrictions and downloads models on-demand:

**macOS:**
```bash
pyinstaller fonixflow_free.spec
```

**Windows:**
```bash
pyinstaller fonixflow_free_windows.spec
```

### Customizing Version Number

Edit the `.spec` files and update:
```python
version='1.0.0',  # Change this
```

### Bundling Whisper Models

To pre-bundle Whisper models (adds 150 MB - 2 GB):

1. Download models:
   ```python
   import whisper
   whisper.load_model("base")  # Repeat for: tiny, small, medium, large-v3
   ```

2. Copy from cache to `assets/models/`:
   ```bash
   # macOS/Linux
   cp ~/.cache/whisper/*.pt assets/models/

   # Windows
   copy %USERPROFILE%\.cache\whisper\*.pt assets\models\
   ```

3. Uncomment model lines in `.spec` files

**Note:** This significantly increases build time and package size.

---

## Build Time Estimates

### First Build
- **macOS:** 10-15 minutes
- **Windows:** 10-20 minutes

### Incremental Builds
- **macOS:** 3-5 minutes
- **Windows:** 3-7 minutes

**Factors:**
- CPU speed
- Disk I/O (SSD recommended)
- Number of dependencies
- Whether models are bundled

---

## Distribution Checklist

### macOS

- [ ] Build completes successfully
- [ ] Test app bundle: `open dist/FonixFlow.app`
- [ ] Verify ffmpeg bundled: `ls dist/FonixFlow.app/Contents/MacOS/ffmpeg`
- [ ] Test DMG installer
- [ ] (Optional) Code sign with Developer ID
- [ ] (Optional) Notarize with Apple

### Windows

- [ ] Build completes successfully
- [ ] Test executable: `dist\FonixFlow.exe`
- [ ] Verify ffmpeg bundled (launches without external ffmpeg)
- [ ] Test on clean Windows machine
- [ ] (Optional) Code sign with certificate
- [ ] (Optional) Create installer with NSIS/Inno Setup

---

## Getting Help

If you encounter issues not covered here:

1. Check the `doc/` folder for additional documentation
2. Review PyInstaller documentation: [pyinstaller.org](https://pyinstaller.org/)
3. Open an issue with:
   - Build command used
   - Full error output
   - Python version: `python --version`
   - PyInstaller version: `pyinstaller --version`
   - Operating system and version

---

## Quick Reference

### macOS

```bash
# Install dependencies
brew install ffmpeg python@3.11
pip3 install -r requirements.txt pyinstaller

# Build
./build_macos.sh

# Outputs
dist/FonixFlow.app
dist/FonixFlow_macOS_Universal.dmg
```

### Windows

```cmd
REM Install dependencies
choco install ffmpeg python311
pip install -r requirements.txt pyinstaller

REM Build
build_windows.bat

REM Output
dist\FonixFlow.exe
```

---

**Happy Building! 🚀**
