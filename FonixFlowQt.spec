# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app/fonixflow_qt.py'],
    pathex=[],
    binaries=[],
    datas=[('licenses.txt', '.'), ('assets', 'assets'), ('i18n', 'i18n'), ('gui/icons', 'gui/icons')],
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='FonixFlowQt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    icon=['gui/icons/app_icon.icns'],
)
app = BUNDLE(
    exe,
    name='FonixFlowQt.app',
    icon='gui/icons/app_icon.icns',
    bundle_identifier='com.fonixflow.qt',
)
