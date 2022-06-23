from setuptools import setup

setup(
    name = "tgback",
    version = '5.0',
    py_modules = ['app','tools'],
    license = 'MIT',
    description = 'tgback — a program for backing and restoring Telegram accounts',
    author_email = 'thenonproton@pm.me',
    url = 'https://github.com/NotStatilko/tgback',
    download_url = 'https://github.com/NotStatilko/tgback/archive/refs/tags/v5.0.tar.gz',
    install_requires = [
        'pyaes==1.6.1',
        'telethon==1.24.0'
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
        tgback=app:entry
    ''',
)
