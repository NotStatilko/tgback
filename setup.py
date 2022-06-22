from setuptools import setup

setup(
    name = "tgback",
    version = '5.0',
    py_modules = ['app','tools'],
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
