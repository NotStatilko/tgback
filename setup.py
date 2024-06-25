from setuptools import setup
from ast import literal_eval

with open('tgback/version.py', encoding='utf-8') as f:
    version = literal_eval(f.read().split('=')[1].strip())

setup(
    name         = 'tgback',
    version      = version,
    packages     = ['tgback'],
    license      = 'MIT',
    description  = 'tgback — a program for backing and restoring Telegram accounts',
    long_description = open('README.md', encoding='utf-8').read(),
    author_email = 'thenonproton@pm.me',
    url          = 'https://github.com/NotStatilko/tgback',
    download_url = f'https://github.com/NotStatilko/tgback/archive/refs/tags/v{version}.tar.gz',

    long_description_content_type='text/markdown',

    package_data = {
        'tgback': ['tgback/data'],
    },
    include_package_data = True,

    keywords = [
        'Telegram', 'Backup', 'CLI',
        'Account', 'Non-official'
    ],
    install_requires = [
        'pyaes==1.6.1',
        'telethon==1.36.0'
    ],
    extras_require = {
        'QR': [
            'qrcode==6.1',
            'pillow==9.0.1',
            'pyzbar==0.1.8'
        ]
    },
    entry_points = '''
        [console_scripts]
        tgback=tgback.app:entry
    ''',
)
