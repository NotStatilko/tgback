# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

if Path.cwd().name != 'pyinstaller':
    raise RuntimeError('You should build App inside the "pyinstaller" folder.')

TGBACK_FOLDER = Path.cwd().parent / 'tgback'
DATA_FOLDER = TGBACK_FOLDER / 'data'

SCRIPT_LOGO = Path.cwd() / 'tgback_logo.ico'
MAIN_SCRIPT = Path.cwd() / '.app_wrapper.py'


PYINSTALLER_DATA: dict = {
    str(Path('data', i.name)): str(i)
    for i in DATA_FOLDER.glob('*')
}
a = Analysis(
    [str(MAIN_SCRIPT)],
    pathex = [],
    binaries = [
        (str(Path('dll', 'libiconv-2.dll')), '.'),
        (str(Path('dll', 'libzbar-32.dll')), '.'),
    ],
    datas = [],
    hiddenimports = [],
    hookspath = [],
    hooksconfig = {},
    runtime_hooks = [],
    excludes = [],
    win_no_prefer_redirects = False,
    win_private_assemblies = False,
    cipher = None,
    noarchive = False
)
for k,v in PYINSTALLER_DATA.items():
    a.datas += [(k, v, 'DATA')]

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher = None
)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas, [],
    name = 'tgback',
    icon = str(SCRIPT_LOGO),
    debug = False,
    bootloader_ignore_signals = False,
    strip = False,
    upx = True,
    upx_exclude = [],
    runtime_tmpdir = None,
    console = True,
    disable_windowed_traceback = False,
    target_arch = None,
    codesign_identity = None,
    entitlements_file = None
)
