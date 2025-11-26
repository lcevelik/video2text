# -*- mode: python ; coding: utf-8 -*-
"""
Linux-specific PyInstaller spec file for FonixFlow.

This spec file creates a standalone Linux executable with:
- All required dependencies bundled
- FFmpeg binary included (if found)
- Proper Linux desktop integration
- All required assets and dependencies

Build with: pyinstaller fonixflow_qt_linux.spec
"""

import os
import sys
import shutil
from pathlib import Path

app_name = 'FonixFlow'

# License file (local validation)
license_file = 'licenses.txt'

# Detect ffmpeg and ffprobe locations (Linux common paths)
ffmpeg_paths = [
    '/usr/bin/ffmpeg',
    '/usr/local/bin/ffmpeg',
    '/opt/ffmpeg/bin/ffmpeg',
    os.path.expanduser('~/bin/ffmpeg'),
]

ffprobe_paths = [
    '/usr/bin/ffprobe',
    '/usr/local/bin/ffprobe',
    '/opt/ffmpeg/bin/ffprobe',
    os.path.expanduser('~/bin/ffprobe'),
]

# Try to find ffmpeg in PATH first
ffmpeg_binary = shutil.which('ffmpeg')
ffprobe_binary = shutil.which('ffprobe')

# If not in PATH, check common installation locations
if not ffmpeg_binary:
    for path in ffmpeg_paths:
        if os.path.exists(path):
            ffmpeg_binary = path
            break

if not ffprobe_binary:
    for path in ffprobe_paths:
        if os.path.exists(path):
            ffprobe_binary = path
            break

binaries = []
if ffmpeg_binary:
    binaries.append((ffmpeg_binary, '.'))
    print(f"✓ Found ffmpeg at: {ffmpeg_binary}")
else:
    print("⚠️ Warning: ffmpeg not found in PATH or standard locations")
    print("  Install with: sudo apt-get install ffmpeg  (Debian/Ubuntu)")
    print("                sudo yum install ffmpeg      (RHEL/CentOS)")
    print("                sudo pacman -S ffmpeg        (Arch)")

if ffprobe_binary:
    binaries.append((ffprobe_binary, '.'))
    print(f"✓ Found ffprobe at: {ffprobe_binary}")
else:
    print("⚠️ Warning: ffprobe not found in PATH or standard locations")
    print("  Install with: sudo apt-get install ffmpeg  (Debian/Ubuntu)")

# Include local license file for offline validation
if os.path.exists(license_file):
    binaries.append((license_file, '.'))

# Try to find and bundle libxcb-cursor (required for Qt xcb platform plugin on Qt 6.5+)
libxcb_cursor_paths = [
    '/usr/lib/x86_64-linux-gnu/libxcb-cursor.so.0',
    '/usr/lib/x86_64-linux-gnu/libxcb-cursor.so',
    '/usr/lib/libxcb-cursor.so.0',
    '/usr/lib/libxcb-cursor.so',
    # Also check in extracted package location (if build script extracted it)
    '/tmp/xcb-cursor-extract/usr/lib/x86_64-linux-gnu/libxcb-cursor.so.0',
]
libxcb_cursor = None
for path in libxcb_cursor_paths:
    if os.path.exists(path):
        libxcb_cursor = path
        break

if libxcb_cursor:
    binaries.append((libxcb_cursor, '.'))
    print(f"✓ Found libxcb-cursor at: {libxcb_cursor}")
else:
    print("⚠️ Warning: libxcb-cursor not found")
    print("  Attempting to download and extract from package...")
    # Try to download and extract the package
    import subprocess
    import tempfile
    try:
        temp_dir = tempfile.mkdtemp()
        deb_file = os.path.join(temp_dir, 'libxcb-cursor0.deb')
        result = subprocess.run(['apt', 'download', 'libxcb-cursor0'], 
                              capture_output=True, text=True, cwd=temp_dir)
        if result.returncode == 0:
            # Find the downloaded .deb file
            for file in os.listdir(temp_dir):
                if file.endswith('.deb'):
                    deb_file = os.path.join(temp_dir, file)
                    extract_dir = os.path.join(temp_dir, 'extract')
                    os.makedirs(extract_dir, exist_ok=True)
                    subprocess.run(['dpkg-deb', '-x', deb_file, extract_dir], check=True)
                    # Look for the library
                    lib_path = os.path.join(extract_dir, 'usr/lib/x86_64-linux-gnu/libxcb-cursor.so.0')
                    if os.path.exists(lib_path):
                        libxcb_cursor = lib_path
                        binaries.append((libxcb_cursor, '.'))
                        print(f"✓ Downloaded and extracted libxcb-cursor from package")
                        break
    except Exception as e:
        print(f"  Could not auto-download: {e}")
        print("  Install with: sudo apt-get install libxcb-cursor0  (Debian/Ubuntu)")
        print("  This library is required for Qt xcb platform plugin on Qt 6.5+")

hiddenimports = [
    # Core Python modules
    'json', 'platform', 'logging', 'argparse', 'sys', 'os',
    # Scientific computing
    'numpy', 'numpy.core', 'numpy.lib.format',
    # scipy is optional - only include if available
    # 'scipy', 'scipy.io', 'scipy.io.wavfile',
    # Audio processing
    'sounddevice', 'soundfile', 'pydub', 'librosa',
    # PyTorch and Whisper
    'torch', 'torch._C', 'whisper', 'tqdm', 'tiktoken',
    # PySide6/Qt
    'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
    'PySide6.QtSvg', 'PySide6.QtMultimedia',
    # Application modules
    'app', 'app.fonixflow_qt', 'app.transcriber', 'app.audio_extractor',
    # GUI modules
    'gui', 'gui.main_window', 'gui.theme', 'gui.widgets', 'gui.workers',
    'gui.dialogs', 'gui.utils', 'gui.icons', 'gui.audio_filters', 'gui.vu_meter',
    # License validation dependencies
    'requests', 'pathlib',
    # For Python 3.13+ compatibility
    'pyaudioop',
    'gui.managers', 'gui.managers.theme_manager', 'gui.managers.settings_manager',
    'gui.managers.file_manager',
    # GUI builders and controllers
    'gui.builders', 'gui.controllers',
    # Recording backends (Linux uses sounddevice)
    'gui.recording', 'gui.recording.base', 'gui.recording.audio_processor',
    'gui.recording.sounddevice_backend',
    # Transcription modules
    'transcription', 'transcription.processors', 'transcription.enhanced',
    'transcription.formatters', 'transcription.diagnostics', 'transcription.audio_processing',
    'transcription.language_detection', 'transcription.segmentation',
    'transcription.processors.audio_processor', 'transcription.processors.format_converter',
    'transcription.processors.diagnostics_logger',
]

# Data files to include
datas = [
    # Whisper model assets
    ('assets/mel_filters.npz', 'whisper/assets'),
    ('assets/gpt2.tiktoken', 'whisper/assets'),
    ('assets/multilingual.tiktoken', 'whisper/assets'),
    # App icons and logo
    ('assets/fonixflow_icon.png', 'assets'),
    ('assets/fonixflow_logo.png', 'assets'),
    ('assets/logo.png', 'assets'),  # Logo for GUI top bar
    ('assets/fonixflow.png', 'assets'),
    ('assets/fonixflow_icon.ico', 'assets'),
    # SVG icons for UI
    ('assets/icons/*.svg', 'assets/icons'),
    # Translation files (i18n)
    ('i18n', 'i18n'),
]

a = Analysis(
    ['app/fonixflow_qt.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_qt6.py'],  # Add runtime hook for Qt plugin path
    excludes=['tkinter', 'matplotlib', 'IPython', 'notebook'],  # Exclude unused packages
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # Build for current architecture
    icon='assets/fonixflow_icon.png',  # Linux can use PNG icons
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

