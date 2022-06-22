# -*- mode: python ; coding: utf-8 -*-

from os.path import join as path_join

block_cipher = None

a = Analysis([path_join('..', 'app.py')],
             pathex=['..'],
             binaries=[
                (path_join('dll','libiconv-2.dll'),'.'),
                (path_join('dll','libzbar-32.dll'),'.'),
            ],
             datas=[],
             hiddenimports=[],
             hookspath=[],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TelegramBackup',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='tgback_logo.ico')
