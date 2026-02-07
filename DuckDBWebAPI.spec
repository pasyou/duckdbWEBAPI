# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=[
        ('src/DuckDBIncrementalSync.py', 'src'),
        ('src/concurrent_query_processor.py', 'src'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'duckdb',
        'pydantic',
        'threading',
        'asyncio',
        'datetime',
        'typing',
        'os',
        'socket',
        'subprocess',
        'webbrowser',
        'uvicorn.lifespan',
        'uvicorn.logging',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.websockets',
        'uvicorn.server',
        'uvicorn.supervisors',
        'uvicorn.workers',
        'starlette',
        'starlette.applications',
        'starlette.middleware',
        'starlette.routing',
        'starlette.responses',
        'starlette.types',
        'pydantic.main',
        'pydantic.fields',
        'pydantic.validators',
        'pydantic.json',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='DuckDBWebAPI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
