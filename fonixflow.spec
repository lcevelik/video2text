# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Main script
main_script = 'app/fonixflow_qt.py'

# App name
app_name = 'FonixFlow'

# Icon file (use PNG for PyInstaller on Windows)
icon_file = 'assets/fonixflow_icon.ico'

# Hidden imports
hidden_imports = [
    'PySide6',
    'numpy',
    'sounddevice',
    'transcription',
    'gui',
]

# Data files (logo, icon, etc.)
datas = [
    ('assets/fonixflow_logo.png', 'assets'),
    ('assets/fonixflow_icon.png', 'assets'),
    ('assets/fonixflow.png', 'assets'),
    ('assets/mel_filters.npz', 'whisper/assets'),
    ('assets/gpt2.tiktoken', 'whisper/assets'),
    ('assets/multilingual.tiktoken', 'whisper/assets'),
]
a = Analysis([
    main_script
],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=icon_file
)
