# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for LabelStudio
"""

import os
import sys

# Get paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(SPEC))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')

block_cipher = None

a = Analysis(
    [os.path.join(BACKEND_DIR, 'main.py')],
    pathex=[BACKEND_DIR],
    binaries=[],
    datas=[
        # Include Vue build output
        (os.path.join(ROOT_DIR, 'dist'), 'dist'),
    ],
    hiddenimports=[
        # Flask and extensions
        'flask',
        'flask_cors',
        'flask_sqlalchemy',
        'werkzeug',

        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext.baked',

        # Image processing
        'PIL',
        'PIL.Image',
        'cv2',

        # QR Code
        'qrcode',
        'qrcode.image.pil',

        # App modules
        'app',
        'app.models',
        'app.routes',
        'app.services',
        'app.utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'pandas',
        'numpy.testing',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LabelStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window (displays IP address)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT_DIR, 'assets', 'icon.ico') if os.path.exists(os.path.join(ROOT_DIR, 'assets', 'icon.ico')) else None,
)
