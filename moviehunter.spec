# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('app.py', '.'), ('launcher.py', '.'), ('init_db.py', '.'), ('templates', 'templates'), ('static', 'static'), ('data', 'data'), ('schema.sql', '.'), ('requirements.txt', '.')],
    hiddenimports=['mysql.connector', 'mysql.connector.pooling', 'PIL', 'PIL.Image', 'flask', 'numpy', 'pandas', 'hashlib', 'secrets', 'datetime', 'decimal', 'math', 'collections', 'getpass', 'os'],
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
    name='MovieHunter',
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
    name='MovieHunter',
)
