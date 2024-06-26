# -*- mode: python ; coding: utf-8 -*-

from sys import maxsize
from pathlib import Path

from platform import system
from importlib import resources


if Path.cwd().name != 'pyinstaller':
    raise RuntimeError('You should build App inside the "pyinstaller" folder.')

if system() == 'Windows':
    try:
        if hasattr(resources, 'files'): # Python 3.9+
            if maxsize > 2**32: # 64bit
                libiconv = resources.files('pyzbar') / 'libiconv.dll'
                libzbar = resources.files('pyzbar') / 'libzbar-64.dll'
            else: # 32bit
                libiconv = resources.files('pyzbar') / 'libiconv-2.dll'
                libzbar = resources.files('pyzbar') / 'libzbar-32.dll'
        else:
            if maxsize > 2**32: # 64bit
                libiconv = resources.path('pyzbar', 'libiconv.dll').__enter__()
                libzbar = resources.path('pyzbar', 'libzbar-64.dll').__enter__()
            else: # 32bit
                libiconv = resources.path('pyzbar', 'libiconv-2.dll').__enter__()
                libzbar = resources.path('pyzbar', 'libzbar-32.dll').__enter__()

        binaries = [(str(libiconv), '.'), (str(libzbar), '.')]
    except ModuleNotFoundError:
        print(
            '!!! Could not find PyZbar package! '
            'QR features will be NOT available!'
        )
        binaries = []
else:
    binaries = []

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
    pathex = [TGBACK_FOLDER.parent],
    binaries = binaries,
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
