# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

# 项目根目录
project_root = os.path.abspath('.')

# 需要包含的数据文件
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
    ('data', 'data'),
    ('schema.sql', '.'),
    ('requirements.txt', '.'),
    ('app.py', '.'),  # 包含app.py作为数据文件
    ('init_db.py', '.'),
    ('*.md', '.'),
]

# 需要包含的二进制文件
binaries = []

# 隐藏导入的模块
hiddenimports = [
    'mysql.connector',
    'mysql.connector.pooling',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'flask',
    'numpy',
    'pandas',
    'hashlib',
    'secrets',
    'datetime',
    'decimal',
    'math',
    'collections',
    'getpass',
    'os',
]

# 需要收集的包
collect_all = [
    'mysql.connector',
    'PIL',
    'flask',
]

# 排除的模块
excludes = [
    'tkinter',
    'matplotlib',
    'scipy',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
]

# 分析阶段
a = Analysis(
    ['launcher.py'],  # 使用launcher.py作为主入口
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 收集额外的包
for pkg in collect_all:
    a.collect_all(pkg)

# PYZ阶段
pyz = PYZ(
    a.pure, 
    a.zipped_data, 
    cipher=None
)

# EXE阶段
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
    console=True,  # 显示控制台窗口，方便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/images/logo.ico' if os.path.exists('static/images/logo.ico') else None,
)

# COLLECT阶段
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MovieHunter',
)
