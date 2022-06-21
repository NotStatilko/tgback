try:
    from PIL import Image, ImageOps, UnidentifiedImageError
    from pyzbar import pyzbar
    from qrcode import make as make_qr # TODO: remove make_qr
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

QR_ERROR = None if not QR_AVAILABLE else UnidentifiedImageError

from base64 import (
    urlsafe_b64encode, urlsafe_b64decode
)
from os import urandom
from hashlib import scrypt

from time import time, ctime
from datetime import timedelta

from itertools import cycle
from os.path import split as path_split

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


VERSION = 'v5.0'
TelegramClient.__version__ = VERSION

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
        self._API_ID = 1770281
        self._API_HASH = '606e46d3d4a5bc4a9813e95add1bfb01'
        
        self._phone_number = phone_number

        self._TelegramClient = TelegramClient(
            StringSession(session), self._API_ID, self._API_HASH
        )
        self.__notify = (
            '''Your {5}backup has been {0}!\n\nRemember that '''
            '''**every two months** it needs to be refreshed, otherwise you will '''
            '''**lose access** to `{1}`. I created a scheduled message for '''
            '''you a week before the time expires, you will be automatically '''
            '''notified and will have time to refresh it.\n\n'''
            '''`@ {2}:  {3}`\n`@ Will off: {4}`\n`@ TGBACK {6}`'''
        )
    @staticmethod
    def __prepare_user_entity(entity):
        if not entity.username:
            entity.username  = entity.first_name
            entity.last_name = '' if not entity.last_name else entity.last_name
        else:
            entity.username  = '@' + entity.username
            entity.last_name = ''

        return entity

    def connect(self) -> None:
        self._TelegramClient.connect()

    def request_code(self) -> None:
        self._TelegramClient.send_code_request(self._phone_number)

    def login(self, password: str=None, code: int=None) -> None:
        if not self._TelegramClient.is_user_authorized():
            try:
                self._TelegramClient.sign_in(self._phone_number, code)
            except SessionPasswordNeededError:
                self._TelegramClient.sign_in(password=password)

    def logout(self):
        return self._TelegramClient.log_out()

    def request_change_phone_code(self, new_number: str) -> str:
        request = self._TelegramClient(SendChangePhoneCodeRequest(
            phone_number = new_number,
            settings = CodeSettings(allow_flashcall=True,
                current_number=True
            )
        ))
        return request.phone_code_hash

    def resend_code(self, phone_number: str, phone_code_hash: str) -> None:
        self._TelegramClient(ResendCodeRequest(phone_number, phone_code_hash))

    def change_phone(self, code: str, code_hash: str, new_number: str) -> None:
        self._TelegramClient(ChangePhoneRequest(
            phone_number=new_number, phone_code=code,
            phone_code_hash=code_hash
        ))
    def backup(self, password: bytes, filename: str=None) -> str:
        tgback_aes = TgbackAES(password)
        tgback_aes.init()

        filename = (filename if filename else str(int(time()))) + '.tgback'

        user = self._TelegramClient.get_entity('me')
        user = self.__prepare_user_entity(user)

        current_time = time()
        backup_death_at = current_time + 5_356_800

        backup_data = [
            b64encode(tgback_aes._scrypt_key).decode(),
            self._TelegramClient.session.save(), str(backup_death_at),
            b64encode(user.username.encode()).decode(),
            str(user.id), b64encode(user.last_name.encode()).decode()
        ]
        dump(backup_data, filename)

        self._TelegramClient.send_file('me',
            open(filename + '.png','rb'),
            caption=self.__notify.format(
                'created', filename, 'Created', ctime(),
                ctime(backup_death_at),'new ', VERSION
            )
        )
        self._TelegramClient.send_message('me',
            f'Hello! Please, update your backup `{filename}`. \n\n**One week left!!**',
            schedule=timedelta(seconds=4_752_000)
        )
        return filename

    def refresh_backup(self, decoded_restored: list, tgback_file_path: str) -> None:
        backup_death_at = time() + 5_356_800

        user = self._TelegramClient.get_entity('me')
        user = self.__prepare_user_entity(user)

        decoded_restored[2] = backup_death_at
        decoded_restored[3] = user.username
        decoded_restored[4] = user.id
        decoded_restored[5] = user.last_name

        dump(encode_restored(decoded_restored),
            tgback_file_path
        )
        ext = '.png' if not tgback_file_path[-4:] == '.png' else ''
        self._TelegramClient.send_file('me',
            open(tgback_file_path + ext,'rb'),
            caption=self.__notify.format(
                'updated', tgback_file_path, 'Updated',
                ctime(), ctime(backup_death_at),'', VERSION
            )
        )
        backup_name = path_split(tgback_file_path)[-1]
        self._TelegramClient.send_message('me',
            f'Hello! Please, update your backup `{backup_name}`\n\n**One week left!!**',
            schedule=timedelta(seconds=4_752_000)
        )
def dump(encoded_restored: list, tgback_file_path: str):
    encrypted = encrypt_restored(encoded_restored)

    ext = '.png' if not tgback_file_path[-4:] == '.png' else ''
    makeqrcode(encrypted).save(tgback_file_path + ext)

    tgback_file_path = tgback_file_path[:-4] if not ext else tgback_file_path
    with open(tgback_file_path,'wb') as f:
        f.write(reedsolo_encode(encrypted))

def restore(tgback_file_path: str, password: bytes, is_qr=False) -> list:
    if is_qr:
        decrypted = decrypt_restored(b64decode(scanqrcode(tgback_file_path)), password)
    else:
        with open(tgback_file_path,'rb') as f:
            decrypted = decrypt_restored(reedsolo_decode(f.read()), password)

    return decode_restored(decrypted.split(b'|'))

def decode_restored(encoded_restored: list) -> list:
    '''
    Converts all elements in list from bytes
    to the required types and decodes all
    from base64 to correct format.
    '''
    try:
        restored = encoded_restored[:]
        restored[0] = b64decode(restored[0])
        restored[1] = restored[1].decode()
        restored[2] = float(restored[2])
        restored[3] = b64decode(restored[3]).decode()
        restored[4] = int(restored[4])
        restored[5] = b64decode(restored[5]).decode()
    except IndexError:
        raise ValueError('Invalid decrypted restored. Bad decryption?')

    return restored

def encode_restored(decoded_restored: list) -> list:
    restored = decoded_restored[:]
    restored[0] = b64encode(restored[0]).decode()
    restored[2] = str(restored[2])
    restored[3] = b64encode(restored[3].encode()).decode()
    restored[4] = str(restored[4])
    restored[5] = b64encode(restored[5].encode()).decode()

    return restored

def join_restored(encoded_restored: list) -> str:
    return '|'.join(encoded_restored)

def encrypt_restored(encoded_restored: str) -> bytes:
    tgback_aes = TgbackAES(b'no_password')
    tgback_aes.init(b64decode(encoded_restored[0]))
    return tgback_aes.encrypt(join_restored(encoded_restored))

def decrypt_restored(encrypted_joined_restored: bytes, password: bytes) -> bytes:
    tgback_aes = TgbackAES(password)
    tgback_aes.init() # Will take some time
    return tgback_aes.decrypt(encrypted_joined_restored)

def reedsolo_encode(encrypted_backup: bytes) -> bytes:
    return bytes(RSC.encode(encrypted_backup))

def reedsolo_decode(encoded_backup: bytes) -> bytes:
    return bytes(RSC.decode(encoded_backup)[0])

def makeqrcode(encrypted_backup: bytes) -> Image:
    encoded = b64encode(encrypted_backup)
    while len(encoded) % 100: encoded += b' ' # There is problem with scanqrcode, it
    return make_qr(encoded)                   # | can't scan QR codes if they `not len(text) % 100`

def scanqrcode(qrcode_path: str) -> bytes:
    try:
        return pyzbar.decode(Image.open(qrcode_path))[0].data.rstrip()
    except:
        # If dark theme and inverted QR colors
        image = ImageOps.invert(Image.open(qrcode_path).convert('RGB'))
        return pyzbar.decode(image)[0].data.rstrip() 
