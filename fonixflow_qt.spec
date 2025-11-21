# -*- mode: python ; coding: utf-8 -*-


app_name = 'FonixFlow'
a = Analysis(
    ['app/fonixflow_qt.py'],
    pathex=[],
    binaries=[('/opt/homebrew/bin/ffmpeg', '.')],
            datas=[
                # Whisper assets
                ('assets/mel_filters.npz', 'whisper/assets'),
                ('assets/gpt2.tiktoken', 'whisper/assets'),
                ('assets/multilingual.tiktoken', 'whisper/assets'),
                # App icons and logo
                ('assets/fonixflow_icon.png', 'assets'),
                ('assets/fonixflow_logo.png', 'assets'),
                ('assets/fonixflow.png', 'assets'),
                ('assets/fonixflow_icon.ico', 'assets'),
                # All SVG icons
                ('assets/icons/*.svg', 'assets/icons'),
                # Translation files
                ('i18n', 'i18n'),
                # Bundle the entire gui package and subfolders
                ('gui/*.py', 'gui'),
                ('gui/builders/*.py', 'gui/builders'),
                ('gui/controllers/*.py', 'gui/controllers'),
                ('gui/managers/*.py', 'gui/managers'),
                ('gui/recording/*.py', 'gui/recording'),
            ],
    hiddenimports=['json', 'platform', 'numpy', 'pydub', 'PySide6.QtSvg', 'app', 'app.transcriber', 'torch', 'whisper', 'sounddevice', 'ScreenCaptureKit', 'AVFoundation', 'Cocoa', 'transcription', 'transcription.processors', 'transcription.enhanced', 'gui', 'gui.main_window', 'gui.theme', 'gui.widgets', 'gui.workers', 'gui.dialogs', 'gui.utils', 'gui.managers', 'gui.icons', 'gui.recording'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    icon='assets/fonixflow_icon.png',
    bundle_identifier='com.fonixflow.qt',
    info_plist={
        'CFBundleName': 'FonixFlow',
        'CFBundleDisplayName': 'FonixFlow',
        'CFBundleIdentifier': 'com.fonixflow.qt',
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSMicrophoneUsageDescription': 'FonixFlow needs microphone access to record your voice.',
        'NSScreenCaptureUsageDescription': 'FonixFlow needs screen recording permission to capture system audio.',
        'LSMinimumSystemVersion': '12.3',
        'LSMultipleInstancesProhibited': True,
    },
)
