# -*- mode: python ; coding: utf-8 -*-
import platform
from pathlib import Path


block_cipher = None

APP_MODULE_PATH = Path('mdiff/visualisation/gui_tkinter/main.py')

a = Analysis([str(APP_MODULE_PATH)],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='mdiff',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mdiff')

if platform.system() == 'Darwin':
    print('Building for macos')
    app = BUNDLE(coll,
                 version=VERSION,
                 name='mdiff.app',
                 icon=None,
                 bundle_identifier=None)