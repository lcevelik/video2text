# -*- mode: python ; coding: utf-8 -*-
"""
Windows-specific PyInstaller spec file for FonixFlow.

This spec file creates a standalone Windows executable with:
- All required dependencies bundled
- FFmpeg binary included
- Proper Windows manifest and icon
- No console window (GUI-only)

Build with: pyinstaller fonixflow_qt_windows.spec
"""

import os
import sys
from pathlib import Path


app_name = 'FonixFlow'

# License file (local validation)
license_file = 'licenses.txt'

# Detect ffmpeg and ffprobe locations (Windows common paths)
ffmpeg_paths = [
    'C:\\ffmpeg\\bin\\ffmpeg.exe',  # Common manual installation
    'C:\\ProgramData\\chocolatey\\bin\\ffmpeg.exe',  # Chocolatey
    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'ffmpeg', 'bin', 'ffmpeg.exe'),
]

ffprobe_paths = [
    'C:\\ffmpeg\\bin\\ffprobe.exe',
    'C:\\ProgramData\\chocolatey\\bin\\ffprobe.exe',
    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'ffmpeg', 'bin', 'ffprobe.exe'),
    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'ffmpeg', 'bin', 'ffprobe.exe'),
]

# Try to find ffmpeg in PATH first
import shutil
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
    print("  Download from: https://ffmpeg.org/download.html#build-windows")
    print("  Extract to C:\\ffmpeg and add C:\\ffmpeg\\bin to PATH")

if ffprobe_binary:
    binaries.append((ffprobe_binary, '.'))
    print(f"✓ Found ffprobe at: {ffprobe_binary}")
else:
    print("⚠️ Warning: ffprobe not found in PATH or standard locations")
    print("  Download from: https://ffmpeg.org/download.html#build-windows")

# Include local license file for offline validation
binaries.append((license_file, '.'))

hiddenimports = [
    # Core Python modules
    'json', 'platform', 'logging', 'argparse', 'sys', 'os',
    # Scientific computing
    'numpy', 'numpy.core', 'numpy.core._methods', 'numpy.lib.format',
    'scipy', 'scipy.io', 'scipy.io.wavfile',
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
    'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
    'PySide6.QtSvg', 'PySide6.QtMultimedia',
    # Application modules
    'app', 'app.fonixflow_qt', 'app.transcriber', 'app.audio_extractor',
    # GUI modules
    'gui', 'gui.main_window', 'gui.theme', 'gui.widgets', 'gui.workers',
    'gui.dialogs', 'gui.utils', 'gui.icons', 'gui.audio_filters', 'gui.vu_meter',
    # GUI managers
    'gui.managers', 'gui.managers.theme_manager', 'gui.managers.settings_manager',
    'gui.managers.file_manager',
    # GUI builders and controllers
    'gui.builders', 'gui.controllers',
    # Recording backends
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
    # Whisper model files (all supported)
    ('assets/models/tiny.pt', 'whisper/assets'),
    ('assets/models/tiny.en.pt', 'whisper/assets'),
    ('assets/models/base.pt', 'whisper/assets'),
    ('assets/models/base.en.pt', 'whisper/assets'),
    ('assets/models/small.pt', 'whisper/assets'),
    ('assets/models/small.en.pt', 'whisper/assets'),
    ('assets/models/medium.pt', 'whisper/assets'),
    ('assets/models/medium.en.pt', 'whisper/assets'),
    ('assets/models/large-v3.pt', 'whisper/assets'),
    # App icons and logo
    ('assets/fonixflow_icon.png', 'assets'),
    ('assets/fonixflow_logo.png', 'assets'),
    ('assets/fonixflow.png', 'assets'),
    ('assets/fonixflow_icon.ico', 'assets'),
    # SVG icons for UI
    ('assets/icons/*.svg', 'assets/icons'),
    # Translation files (i18n)
    ('i18n', 'i18n'),
    # Do not include raw .py files; let PyInstaller package and compile them as .pyc
]

a = Analysis(
    ['app/fonixflow_qt.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    upx=False,  # Disable UPX to avoid antivirus false positives
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # Build for current architecture (x86_64)
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/fonixflow_icon.ico',  # Windows icon file
    version=None,  # Can add version info resource here
    uac_admin=False,  # Don't require admin privileges
    uac_uiaccess=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,  # Disable UPX to avoid antivirus false positives
    upx_exclude=[],
    name=app_name,
)
