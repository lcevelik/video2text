# -*- mode: python ; coding: utf-8 -*-
"""
macOS-specific PyInstaller spec file for FonixFlow.

This spec file creates a native macOS .app bundle with:
- Native system audio capture via ScreenCaptureKit (macOS 12.3+)
- Proper code signing and entitlements
- All required assets and dependencies
- Microphone and screen recording permissions

Build with: pyinstaller fonixflow_qt.spec
"""

import os
import sys
from pathlib import Path

# Application name
app_name = 'FonixFlow'

# Detect ffmpeg and ffprobe locations (supports both Apple Silicon and Intel Macs)
ffmpeg_paths = [
    '/opt/homebrew/bin/ffmpeg',  # Apple Silicon (M1/M2)
    '/usr/local/bin/ffmpeg',      # Intel Mac (Homebrew)
    '/opt/local/bin/ffmpeg',      # MacPorts
]
ffprobe_paths = [
    '/opt/homebrew/bin/ffprobe',  # Apple Silicon (M1/M2)
    '/usr/local/bin/ffprobe',     # Intel Mac (Homebrew)
    '/opt/local/bin/ffprobe',     # MacPorts
]

ffmpeg_binary = None
for path in ffmpeg_paths:
    if os.path.exists(path):
        ffmpeg_binary = path
        break

ffprobe_binary = None
for path in ffprobe_paths:
    if os.path.exists(path):
        ffprobe_binary = path
        break

binaries = []
if ffmpeg_binary:
    binaries.append((ffmpeg_binary, '.'))
    print(f"✓ Found ffmpeg at: {ffmpeg_binary}")
else:
    print("⚠ Warning: ffmpeg not found in standard locations")
    print("  Install with: brew install ffmpeg")

if ffprobe_binary:
    binaries.append((ffprobe_binary, '.'))
    print(f"✓ Found ffprobe at: {ffprobe_binary}")
else:
    print("⚠ Warning: ffprobe not found in standard locations")
    print("  Install with: brew install ffmpeg")

# Hidden imports - comprehensive list for all dependencies
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
    # macOS-specific frameworks (optional, for native system audio)
    'objc', 'Foundation', 'Cocoa', 'AVFoundation', 'ScreenCaptureKit',
    # Application modules
    'app', 'app.fonixflow_qt', 'app.transcriber', 'app.audio_extractor', 'app.macos_permissions',
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
    'gui.recording.sounddevice_backend', 'gui.recording.screencapturekit_backend',
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
    ('assets/fonixflow.png', 'assets'),
    ('assets/fonixflow_icon.ico', 'assets'),
    # SVG icons for UI
    ('assets/icons/*.svg', 'assets/icons'),
    # Translation files (i18n)
    ('i18n', 'i18n'),
    # Python source files for gui package (needed for dynamic imports) package as module
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
    upx=True,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,  # Disable macOS argv emulation to prevent multiple instances/multiprocessing issues
    target_arch=None,  # Build for current architecture (x86_64 or arm64)
    codesign_identity=None,  # Set to your Apple Developer ID for distribution
    entitlements_file='entitlements.plist',  # Required for microphone/screen recording
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

# Check for .icns icon file (preferred) or fall back to PNG
icon_file = 'assets/fonixflow_icon.icns'
if not os.path.exists(icon_file):
    icon_file = 'assets/fonixflow_icon.png'
    print("⚠ Warning: Using PNG icon. For better quality, convert to .icns:")
    print("  mkdir FonixFlow.iconset")
    print("  sips -z 16 16     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_16x16.png")
    print("  sips -z 32 32     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_16x16@2x.png")
    print("  sips -z 32 32     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_32x32.png")
    print("  sips -z 64 64     assets/fonixflow_icon.png --out FonixFlow.iconset/icon_32x32@2x.png")
    print("  sips -z 128 128   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_128x128.png")
    print("  sips -z 256 256   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_128x128@2x.png")
    print("  sips -z 256 256   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_256x256.png")
    print("  sips -z 512 512   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_256x256@2x.png")
    print("  sips -z 512 512   assets/fonixflow_icon.png --out FonixFlow.iconset/icon_512x512.png")
    print("  sips -z 1024 1024 assets/fonixflow_icon.png --out FonixFlow.iconset/icon_512x512@2x.png")
    print("  iconutil -c icns FonixFlow.iconset -o assets/fonixflow_icon.icns")

app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    icon=icon_file,
    bundle_identifier='com.fonixflow.qt',
    version='1.0.0',  # Update this with your app version
    info_plist={
        # Basic app information
        'CFBundleName': app_name,
        'CFBundleDisplayName': app_name,
        'CFBundleIdentifier': 'com.fonixflow.qt',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 FonixFlow',

        # macOS integration
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'LSMinimumSystemVersion': '12.3',  # macOS 12.3+ required for ScreenCaptureKit
        'LSMultipleInstancesProhibited': True,  # Prevent multiple instances (enforced by code too)

        # Required permissions with user-facing descriptions
        'NSMicrophoneUsageDescription': 'FonixFlow needs microphone access to record your voice for transcription.',
        'NSScreenCaptureUsageDescription': 'FonixFlow needs screen recording permission to capture system audio from applications.',

        # Document types (optional - for drag & drop support)
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Audio Files',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': [
                    'public.audio',
                    'public.mp3',
                    'public.mpeg-4-audio',
                    'com.microsoft.waveform-audio',
                ],
            },
            {
                'CFBundleTypeName': 'Video Files',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': [
                    'public.movie',
                    'public.video',
                    'public.mpeg-4',
                ],
            },
        ],

        # Dark mode support
        'NSRequiresAquaSystemAppearance': False,
    },
)
