# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_qt.py'],
    pathex=[],
    binaries=[],
    datas=[('ffmpeg.exe', '.'), ('gui', 'gui'), ('transcription', 'transcription'), ('requirements.txt', '.'), ('_internal\\whisper\\assets\\mel_filters.npz', '_internal\\whisper\\assets'), ('.\\venv\\Lib\\site-packages\\PySide6\\plugins', 'PySide6\\plugins')],
    hiddenimports=['PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtNetwork', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtPrintSupport', 'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickControls2', 'PySide6.QtSvg', 'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebChannel', 'PySide6.QtWebSockets', 'pydub', 'whisper', 'sounddevice', 'comtypes'],
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
    name='gui_qt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='gui_qt',
)
