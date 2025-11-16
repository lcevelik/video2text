# 🚀 Packaging Quick Start

## TL;DR - One Command Does Everything!

```bash
# BEST QUALITY (~3.5GB) - Recommended if you don't care about size
python package_app.py --quality best

# BALANCED (~1.2GB)
python package_app.py --quality balanced

# LIGHTWEIGHT (~500MB)
python package_app.py --quality lightweight
```

**That's it!** The script will:
1. ✅ Download and bundle Whisper models
2. ✅ Download and bundle FFmpeg binaries
3. ✅ Build self-contained executable
4. ✅ Create distribution package

**Result:** Folder in `dist/` that users can run **without installing anything**!

---

## What You Get

After running the command, you'll have:

```
dist/Video2Text_Qt/
├── Video2Text_Qt.exe          # Main executable (Windows)
├── Video2Text_Qt              # Main executable (Linux/Mac)
├── launch.bat / launch.sh     # Launcher with FFmpeg
├── ffmpeg/                    # FFmpeg binaries
├── bundled_models/            # Whisper models
├── _internal/                 # Python + dependencies
└── README.txt                 # User instructions
```

**Total size:** 500MB to 3.5GB depending on model choice

---

## Distribution

### 1. Test It First
```bash
cd dist/Video2Text_Qt/
./Video2Text_Qt  # or Video2Text_Qt.exe on Windows
```

### 2. Create Archive
```bash
# Linux/Mac
zip -r Video2Text_Complete.zip dist/Video2Text_Qt/

# Windows
Compress-Archive -Path dist\Video2Text_Qt -DestinationPath Video2Text.zip
```

### 3. Give to Users
Users just:
1. Unzip
2. Double-click the executable
3. Done! Works completely offline!

---

## Model Quality Comparison

| Preset | Models | Size | Quality | Best For |
|--------|--------|------|---------|----------|
| **best** | large | ~3.5GB | ⭐⭐⭐⭐⭐ | Maximum accuracy |
| balanced | medium | ~1.2GB | ⭐⭐⭐⭐ | Professional use |
| lightweight | base | ~500MB | ⭐⭐⭐ | Quick transcription |

**Since you don't care about size:** Use `--quality best`!

---

## Advanced Options

### Choose Specific Models
```bash
# Bundle multiple model sizes (users choose in app)
python package_app.py --models base medium large
```

### Choose GUI Version
```bash
# Qt GUI (recommended - modern)
python package_app.py --quality best --gui qt

# Enhanced Tkinter
python package_app.py --quality best --gui enhanced

# Original Tkinter
python package_app.py --quality best --gui original
```

### Single File Mode
```bash
# Single .exe instead of folder (slower startup)
python package_app.py --quality best --onefile
```

---

## Manual Two-Step Process

If you prefer manual control:

### Step 1: Bundle Models
```bash
python bundle_models_enhanced.py --models large
```

### Step 2: Build Package
```bash
python build_standalone_enhanced.py --bundle-all --gui qt
```

---

## Requirements (for building)

**On your machine (to build the package):**
- Python 3.8+
- pip packages: `pip install -r requirements.txt`
- PyInstaller: `pip install pyinstaller`

**On user machines (to run the package):**
- ✅ Nothing! Completely self-contained!

---

## Platform-Specific Notes

### Windows
- Works on Windows 10/11
- Produces `.exe` file
- Users just double-click

### Linux
- Tested on Ubuntu 20.04+
- Users may need: `chmod +x Video2Text_Qt`
- Then: `./Video2Text_Qt`

### macOS
- Works on macOS 10.14+
- Users may need to right-click → Open (first time only)
- Bypasses Gatekeeper warning

---

## Troubleshooting

**Build fails with "PyInstaller not found":**
```bash
pip install pyinstaller
```

**Build fails with "Whisper not found":**
```bash
pip install -r requirements.txt
```

**Built app won't run:**
- Check you're on same OS as build (Windows build → Windows users)
- Try using launcher script (launch.bat / launch.sh)
- See full PACKAGING_GUIDE.md

---

## File Size Calculator

| What's Included | Size |
|-----------------|------|
| Base package (Python + deps + FFmpeg) | ~400MB |
| + tiny model | +39MB |
| + base model | +74MB |
| + small model | +244MB |
| + medium model | +769MB |
| + large model | +3GB |
| **ALL models** | **~4.8GB** |

---

## Next Steps

1. **Build your package:**
   ```bash
   python package_app.py --quality best
   ```

2. **Test it:**
   ```bash
   cd dist/Video2Text_Qt/
   ./Video2Text_Qt
   ```

3. **Distribute:**
   - Zip the folder
   - Upload to file sharing
   - Users download, unzip, run!

4. **Read full guide:**
   - See `PACKAGING_GUIDE.md` for detailed instructions
   - Platform-specific tips
   - Distribution best practices

---

## Support

- **Full guide:** PACKAGING_GUIDE.md
- **Issues:** GitHub Issues
- **Documentation:** README.md

---

**Happy packaging! Your users will love not having to install Python! 😊**
