try:
    from PIL import Image, UnidentifiedImageError
    from pyzbar import pyzbar
    from qrcode import make as make_qr
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

QR_ERROR = IndexError if not QR_AVAILABLE else UnidentifiedImageError

try:
    from sys import _MEIPASS
except ImportError:
    _MEIPASS = None

from base64 import (
    urlsafe_b64encode, urlsafe_b64decode
)
from os import urandom
from hashlib import scrypt

from time import time, ctime
from datetime import timedelta

from pickle import (
    loads as pickle_loads,
    dumps as pickle_dumps
)
from pathlib import Path
from itertools import cycle

from telethon.sync import TelegramClient
from telethon.tl.types import CodeSettings
from telethon.sessions import StringSession

from telethon.tl.functions.account import (
    ChangePhoneRequest, SendChangePhoneCodeRequest
)
from telethon.errors import (
    PhoneNumberInvalidError, SessionPasswordNeededError
)
from telethon.tl.functions.auth import ResendCodeRequest

from pyaes import AESModeOfOperationCBC
from pyaes.util import append_PKCS7_padding, strip_PKCS7_padding

from .version import VERSION


ABSPATH: Path = Path(_MEIPASS) if _MEIPASS is not None \
    else Path(__file__).parent

TelegramClient.__version__ = VERSION

# Three months by default
BACKUP_DEATH_IN = 8_040_000


def make_scrypt_key(
        password: bytes,
        salt: bytes,
        n: int=2**20,
        r: int=8,
        p: int=1,
        dklen: int=32) -> bytes:
    """
    Will use 1GB of RAM by default.
    memory = 128 * r * (n + p + 2)
    """
    m = 128 * r * (n + p + 2)
    return scrypt(
        password, n=n, r=r, dklen=32,
        p=p, salt=salt, maxmem=m
    )
class PyaesState:
    def __init__(self, key: bytes, iv: bytes):
        """
        Class to wrap ``pyaes.AESModeOfOperationCBC``

        .. note::
            You should use only ``encrypt()`` or
            ``decrypt()`` method per one object.

        Arguments:
            key (``bytes``):
                AES encryption/decryption Key.

            iv (``bytes``):
                AES Initialization Vector.
        """
        self._aes_state = AESModeOfOperationCBC(
            key = key, iv = iv
        )
        self.__mode = None # encrypt mode is 1 and decrypt is 2

    def encrypt(self, data: bytes) -> bytes:
        """``data`` length must be divisible by 16."""
        if not self.__mode:
            self.__mode = 1
        else:
            if self.__mode != 1:
                raise Exception('You should use only decrypt function.')

        assert not len(data) % 16; total = b''

        for _ in range(len(data) // 16):
            total += self._aes_state.encrypt(data[:16])
            data = data[16:]

        return total

    def decrypt(self, data: bytes) -> bytes:
        """``data`` length must be divisible by 16."""
        if not self.__mode:
            self.__mode = 2
        else:
            if self.__mode != 2:
                raise Exception('You should use only encrypt function.')

        assert not len(data) % 16; total = b''

        for _ in range(len(data) // 16):
            total += self._aes_state.decrypt(data[:16])
            data = data[16:]

        return total

class TelegramAccount:
    def __init__(self, phone_number: str=None, session: str=None):
        self._API_ID = 1770281 # (<V) DO NOT USE THESE!!!
        self._API_HASH = '606e46d3d4a5bc4a9813e95add1bfb01'

        self._phone_number = phone_number

        self.TelegramClient = TelegramClient(
            StringSession(session), self._API_ID, self._API_HASH
        )
        self.__notify = (
            '''Your {5}backup has been {0}!\n\nRemember that **every '''
            '''three months** it needs to be refreshed, otherwise you will '''
            '''**lose access** to `{1}`. We created a scheduled message for '''
            '''you a week before the time expires, you will be automatically '''
            '''notified and will have time to update it.\n\n'''
            '''`@ {2}:  {3}`\n`@ Will off: {4}`\n`@ TGBACK (TelegramBackup) v{6}`'''
        )
    def connect(self) -> None:
        self.TelegramClient.connect()

    def request_code(self) -> None:
        self.TelegramClient.send_code_request(self._phone_number)

    def login(self, password: str=None, code: int=None) -> None:
        if not self.TelegramClient.is_user_authorized():
            try:
                self.TelegramClient.sign_in(self._phone_number, code)
            except SessionPasswordNeededError:
                self.TelegramClient.sign_in(password=password)

    def logout(self):
        return self.TelegramClient.log_out()

    def request_change_phone_code(self, new_number: str) -> str:
        request = self.TelegramClient(SendChangePhoneCodeRequest(
            phone_number = new_number,
            settings = CodeSettings(allow_flashcall=True,
                current_number=True
            )
        ))
        return request.phone_code_hash

    def resend_code(self, phone_number: str, phone_code_hash: str) -> None:
        self.TelegramClient(ResendCodeRequest(phone_number, phone_code_hash))

    def change_phone(self, code: str, code_hash: str, new_number: str) -> None:
        self.TelegramClient(ChangePhoneRequest(
            phone_number=new_number, phone_code=code,
            phone_code_hash=code_hash
        ))
    def backup(self, password: bytes, filename: str=None, refresh: bool=False) -> str:
        backup_salt = urandom(32)
        backup_key = make_scrypt_key(password, backup_salt)

        filename = (filename if filename else str(int(time()))) + '.tgback'

        current_time = time()
        backup_death_at = current_time + BACKUP_DEATH_IN

        backup_dict = {
            'session' : self.TelegramClient.session.save(),
            'death_at': backup_death_at,
        }
        backup_iv = urandom(16)

        backup_data = PyaesState(backup_key, backup_iv).encrypt(
            append_PKCS7_padding(pickle_dumps(backup_dict))
        )
        backup_data = backup_salt + backup_iv + backup_data

        with open(filename, 'wb') as f:
            f.write(backup_data)

        if refresh:
            fformat = ('updated', 'Updated', '')
        else:
            fformat = ('created', 'Created', 'new ')

        if QR_AVAILABLE:
            ext = '' if filename.endswith('.png') else '.png'
            encoded_backup_data = urlsafe_b64encode(backup_data).decode()
            makeqrcode(encoded_backup_data).save(filename + ext)

            self.TelegramClient.send_file(
                'me', open(filename + '.png','rb'),
                caption=self.__notify.format(
                    fformat[0], filename, fformat[1], ctime(),
                    ctime(backup_death_at), fformat[2], VERSION
                )
            )
        else:
            self.TelegramClient.send_message('me',
                self.__notify.format(
                    fformat[0], filename, fformat[1], ctime(),
                    ctime(backup_death_at), fformat[2], VERSION
                )
            )
        self.TelegramClient.send_message(
            'me', f'Hello! Please, update your backup `{filename}`.\n\n**One week left!!**',
            schedule=timedelta(seconds=BACKUP_DEATH_IN-604800)
        )
        return (filename, backup_dict)

def restore(
        tgback_file_path: str,
        password: bytes,
        is_qr: bool=False) -> dict:

    if is_qr:
        backup_data = scanqrcode(tgback_file_path)
    else:
        backup_data = open(tgback_file_path,'rb').read()

    backup_salt = backup_data[:32]
    backup_iv = backup_data[32:48]

    backup_key = make_scrypt_key(password, backup_salt)
    backup_data = PyaesState(backup_key, backup_iv).decrypt(backup_data[48:])

    return pickle_loads(backup_data)

def makeqrcode(data: str):
    # There is problem with scanqrcode, it can't
    # scan QR codes if they `not len(text) % 100`
    while len(data) % 100:
        data += ' '
    return make_qr(data)

def scanqrcode(qrcode_path: str) -> bytes:
    decoded = pyzbar.decode(Image.open(qrcode_path))[0].data
    return urlsafe_b64decode(decoded.rstrip())
