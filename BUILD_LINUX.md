# Building FonixFlow for Linux

This guide explains how to build FonixFlow as a standalone Linux executable using PyInstaller.

## Prerequisites

### Required System Packages

1. **Python 3.9+** - Usually pre-installed on most Linux distributions
2. **ffmpeg** - For audio/video processing
   ```bash
   sudo apt-get install ffmpeg  # Debian/Ubuntu
   sudo yum install ffmpeg      # RHEL/CentOS/Fedora
   sudo pacman -S ffmpeg        # Arch Linux
   ```

3. **libxcb-cursor0** - Required for Qt 6.5+ xcb platform plugin
   ```bash
   sudo apt-get install libxcb-cursor0  # Debian/Ubuntu
   sudo yum install libxcb-cursor        # RHEL/CentOS/Fedora
   sudo pacman -S libxcb-cursor          # Arch Linux
   ```

### Python Dependencies

Install Python dependencies:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

Or use the build script which will install them automatically.

## Quick Build

The easiest way to build is using the provided build script:

```bash
./build_linux.sh
```

This script will:
- Check all prerequisites
- Clean previous builds
- Build the executable with PyInstaller
- Show instructions for running the app

## Manual Build

If you prefer to build manually:

```bash
pyinstaller fonixflow_qt_linux.spec
```

## Running the Application

After building, run the application:

```bash
./dist/FonixFlow/FonixFlow
```

## Troubleshooting

### Qt Platform Plugin Error

If you see this error:
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**Solution:** Install `libxcb-cursor0`:
```bash
sudo apt-get install libxcb-cursor0
```

Then rebuild the application.

### Missing FFmpeg

If ffmpeg is not found during build, the app will still build but audio/video processing features may not work. Install ffmpeg and rebuild.

### Desktop Entry

To create a desktop entry for easy launching, create `~/.local/share/applications/fonixflow.desktop`:

```ini
[Desktop Entry]
Name=FonixFlow
Comment=Audio and Video Transcription Tool
Exec=/path/to/dist/FonixFlow/FonixFlow
Icon=/path/to/dist/FonixFlow/assets/fonixflow_icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Video;
```

Replace `/path/to/` with the actual path to your build directory.

## Build Output

The build creates:
- `dist/FonixFlow/FonixFlow` - Main executable
- `dist/FonixFlow/_internal/` - All bundled dependencies and assets

The entire `dist/FonixFlow/` directory can be distributed as a standalone application.

