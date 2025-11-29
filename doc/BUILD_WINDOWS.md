# Building FonixFlow for Windows

This guide explains how to build FonixFlow as a standalone Windows executable using PyInstaller.

## Prerequisites

### Required Software

1. **Windows 10/11** - 64-bit version required
2. **Python 3.9+** - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation
3. **ffmpeg** - Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
   - Extract to `C:\ffmpeg` or add to PATH
4. **PyInstaller** - Install via pip: `pip install pyinstaller`


### Install Python Dependencies

```cmd
pip install -r requirements.txt
```

### License System

FonixFlow supports both offline and online license validation:

- Add your license key to `licenses.txt` for offline use
- If not found locally, the app checks LemonSqueezy API

## Quick Build

The easiest way to build is using the provided build script:

```cmd
build_windows.bat
```

This script will:
- Check all prerequisites
- Clean previous builds
- Build the .exe executable
- Show instructions for installation

## Manual Build

If you prefer to build manually:


### 1. Build with PyInstaller

```cmd
pyinstaller fonixflow_qt_windows.spec
```

Make sure `licenses.txt` is present in the app folder to enable offline license validation.

The build process will:
- Analyze dependencies from `app/fonixflow_qt.py`
- Bundle all Python packages and native libraries
- Include ffmpeg binary (from PATH or common locations)
- Package all assets (icons, translations, Whisper model files)
- Create a standalone executable

### 2. Run the Application

```cmd
dist\FonixFlow\FonixFlow.exe
```

Or create a shortcut to the executable for easy access.

## Understanding the .spec File

The `fonixflow_qt_windows.spec` file is specifically configured for Windows with these features:

### FFmpeg Detection

The spec file automatically detects ffmpeg from multiple locations:
- `C:\ffmpeg\bin\ffmpeg.exe` (common manual installation)
- `C:\ProgramData\chocolatey\bin\ffmpeg.exe` (Chocolatey)
- System PATH

### Hidden Imports

Comprehensive list of all required modules:
- **Core**: Python standard library modules
- **Scientific**: NumPy, SciPy for audio processing
- **Audio**: sounddevice, soundfile, pydub, librosa
- **ML**: PyTorch, Whisper, tiktoken
- **GUI**: PySide6/Qt with SVG support
- **App Modules**: All gui, transcription, and app packages

### Data Files

Includes all necessary assets:
- Whisper model tokenizer files (mel_filters.npz, tiktoken files)
- Application icons (PNG, ICO)
- SVG icons for UI elements
- Translation files (i18n folder)
- Python source files for dynamic imports

### Windows-Specific Configuration

- **Console**: Set to `False` to hide console window (GUI-only app)
- **Icon**: Uses `assets/fonixflow_icon.ico` for the executable
- **UPX**: Disabled for better compatibility
- **Manifest**: Includes UAC settings and DPI awareness

## Creating an Installer

### Using Inno Setup (Recommended)

1. Download and install [Inno Setup](https://jrsoftware.org/isinfo.php)

2. Create an installer script (`installer.iss`):

```iss
[Setup]
AppName=FonixFlow
AppVersion=1.0
DefaultDirName={pf}\FonixFlow
DefaultGroupName=FonixFlow
OutputDir=dist
OutputBaseFilename=FonixFlow-Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\FonixFlow\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\FonixFlow"; Filename: "{app}\FonixFlow.exe"
Name: "{commondesktop}\FonixFlow"; Filename: "{app}\FonixFlow.exe"

[Run]
Filename: "{app}\FonixFlow.exe"; Description: "Launch FonixFlow"; Flags: postinstall nowait skipifsilent
```

3. Compile the installer:
```cmd
iscc installer.iss
```

### Using NSIS

Alternatively, use [NSIS](https://nsis.sourceforge.io/):

```nsis
!define APPNAME "FonixFlow"
!define COMPANYNAME "FonixFlow"
!define DESCRIPTION "Audio Transcription Tool"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0

InstallDir "$PROGRAMFILES\${APPNAME}"
Name "${APPNAME}"
OutFile "dist\FonixFlow-Setup.exe"

Section "Install"
    SetOutPath $INSTDIR
    File /r "dist\FonixFlow\*.*"
    
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\FonixFlow.exe"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\FonixFlow.exe"
SectionEnd
```

## Troubleshooting

### Build Fails with Missing Module

If PyInstaller can't find a module, add it to the `hiddenimports` list in `fonixflow_qt_windows.spec`:

```python
hiddenimports=[
    # ... existing imports ...
    'your_missing_module',
]
```

### App Crashes on Launch

1. Run from Command Prompt to see error messages:
   ```cmd
   dist\FonixFlow\FonixFlow.exe
   ```

2. Check if all dependencies are included:
   ```cmd
   pyinstaller --log-level=DEBUG fonixflow_qt_windows.spec
   ```

### FFmpeg Not Found

The spec file should auto-detect ffmpeg, but if it doesn't:

1. Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH environment variable
4. Or update `fonixflow_qt_windows.spec` with the correct path

### Missing DLL Errors

If you get errors about missing DLLs:

```cmd
pip install --force-reinstall torch torchaudio
pip install --force-reinstall PySide6
```

### Antivirus False Positives

Some antivirus software may flag PyInstaller executables as suspicious. This is a known issue with PyInstaller. You can:
- Add an exception for the executable
- Submit the file to your antivirus vendor as a false positive
- Code sign the executable (requires a code signing certificate)

## Code Signing (Optional)

For distribution, you should code sign your executable to avoid Windows SmartScreen warnings:

1. Obtain a code signing certificate from a trusted CA (e.g., DigiCert, Sectigo)

2. Sign the executable using `signtool` (included with Windows SDK):

```cmd
signtool sign /f "certificate.pfx" /p "password" /t http://timestamp.digicert.com dist\FonixFlow\FonixFlow.exe
```

Or use a hardware token:

```cmd
signtool sign /n "Your Company Name" /t http://timestamp.digicert.com dist\FonixFlow\FonixFlow.exe
```

## File Structure

After building, the distribution structure is:

```
dist\FonixFlow\
├── FonixFlow.exe           # Main executable
├── ffmpeg.exe              # Bundled ffmpeg binary
├── ffprobe.exe             # Bundled ffprobe binary
├── assets\                 # Icons, images
├── i18n\                   # Translations
├── gui\                    # GUI modules
├── whisper\                # Whisper model files
├── _internal\              # Python runtime and dependencies
│   ├── python39.dll
│   ├── torch\
│   ├── PySide6\
│   └── ... (other dependencies)
```

## Performance Optimization

### Reducing Executable Size

1. **Exclude unused modules**: Edit `excludes` in the spec file
2. **Use UPX compression**: Set `upx=True` in the spec file (may cause antivirus issues)
3. **Remove debug symbols**: Use `--strip` flag

### Faster Startup

1. **Lazy imports**: Import heavy modules only when needed
2. **Precompiled bytecode**: PyInstaller does this automatically
3. **SSD installation**: Recommend users install on SSD for faster loading

## Distribution Checklist

Before distributing your application:

- [ ] Test on a clean Windows installation (VM recommended)
- [ ] Verify all features work (microphone access, file loading, transcription)
- [ ] Check file associations work correctly
- [ ] Test installer/uninstaller
- [ ] Code sign the executable
- [ ] Create user documentation
- [ ] Test on Windows 10 and Windows 11
- [ ] Verify antivirus compatibility

## Further Reading

- [PyInstaller Windows Documentation](https://pyinstaller.org/en/stable/operating-mode.html#windows)
- [Windows Code Signing Guide](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
