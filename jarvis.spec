# PyInstaller spec for JARVIS .exe (Windows) — one file, double-click to run.
# Build locally:  pip install pyinstaller  &&  pyinstaller jarvis.spec
# Or push a v1.0.0 tag to GitHub — the release workflow builds it automatically.
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(
    ['jarvis_server.py'],
    pathex=[],
    binaries=[],
    datas=[('ui', 'ui'), ('config.json', '.')],
    hiddenimports=['jarvis', 'brain', 'power_pack', 'file_ops', 'listen', 'windows_pack'],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    win_no_prefer_redirects=False, win_private_assemblies=False,
    cipher=block_cipher, noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [],
          name='Jarvis', debug=False, bootloader_ignore_signals=False,
          strip=False, upx=True, console=False, icon=None)
