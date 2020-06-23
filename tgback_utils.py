from PIL import Image
from os import urandom
from itertools import cycle
from time import time, ctime
from datetime import timedelta
from os.path import split as path_split
from base64 import b64encode, b64decode

from telethon import TelegramClient
from telethon.tl.types import CodeSettings
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError, SessionPasswordNeededError
)
from telethon.tl.functions.account import (
    ChangePhoneRequest, SendChangePhoneCodeRequest
)
from pyzbar import pyzbar
from reedsolo import RSCodec
from qrcode import make as make_qr

from pyaes import AESModeOfOperationCBC, Encrypter, Decrypter
from pyaes.util import append_PKCS7_padding, strip_PKCS7_padding

from hashlib import algorithms_guaranteed

hash_functions = []
for i in algorithms_guaranteed: # Imports all guaranteed hash_functions
    exec(f'from hashlib import {i}; hash_functions.append({i})')

hash_functions.sort(key=repr)
hash_functions *= 20

VERSION = 'v3.0 beta(2.0)'
TelegramClient.__version__ = VERSION

RSC = RSCodec(222)


class TgbackAES:
    def __init__(self, password: bytes, iv: bytes=None):
        if not isinstance(password, bytes):
            password = password.encode()

        self.__raw_password = password
        self.__password_hash = None
        self.__iv = urandom(16) if not iv else iv

    @staticmethod
    def _hash_password(password: bytes, iter_count=2_222_222) -> sha3_256:
        salt = (
            b'''\xcdVno\xc7\xeey7\x84\xfb^\xba\x8d\\\x1e'''
            b'''\xdfm-\xf3(?\xa3\x1fN|\x1e\xe2\x8f\x93\xe1'''
            b'''\x81}\xc3\x8e^\xd7\xfc\x03\x92\xc3\x83\xd3'''
            b'''\xb5\xb8#\xa3\x90\xf1Y\xabT}M\x1f\xc5\x97R/'''
            b'''\xd7\n\xd5\xe3\xf9\xb3b\xc3Y\\\xb3\x1dj]v'6'''
        )
        mainhash = sha512(password + salt).digest()
        mainhashfuncs = cycle((hash_functions[i] for i in mainhash))

        hashed = sha512(mainhash).digest()
        for _ in range(iter_count):
            hash_function = next(mainhashfuncs)
            try:
                hashed = hash_function(hashed)
                hashed = hashed.digest()
            except TypeError: # SHAKE requires digest size
                hashed = hashed.digest(64)

        return sha3_256(hashed)

    def init(self, password_hash: bytes=None) -> None:
        if password_hash:
            self._password_hash = password_hash
        else:
            if not self.__raw_password:
                raise Exception('Already initialized')
            else:
                self._password_hash = self._hash_password(self.__raw_password).digest()
                self.__raw_password = None

    def encrypt(self, data: bytes) -> bytes:
        if not self._password_hash:
            raise Exception('You need to call .init() for first')
        else:
            if not isinstance(data, bytes):
                data = data.encode()

            if len(data) % 16:
                data = append_PKCS7_padding(data)

            aes_cbc = Encrypter(
                AESModeOfOperationCBC(
                    self._password_hash, self.__iv)
            )
            encrypted =  aes_cbc.feed(data)
            encrypted += aes_cbc.feed()
            encrypted += self.__iv # LAST 16 BYTES OF ENCRYPTED DATA IS IV !
            return encrypted

    def decrypt(self, edata: bytes) -> bytes:
        if not self._password_hash:
            raise Exception('You need to call .init() for first')

        elif not isinstance(edata, bytes):
            raise Exception('edata must be bytes')
        else:
            iv = edata[-16:]; edata = edata[:-16] # LAST 16 BYTES OF ENCRYPTED DATA IS IV !
            aes_cbc = Decrypter(AESModeOfOperationCBC(self._password_hash, iv))
            decrypted = aes_cbc.feed(edata); decrypted += aes_cbc.feed()
            return strip_PKCS7_padding(decrypted)

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
            '''**every two months** it needs to be updated, otherwise you will '''
            '''**lose access** to `{1}`. I created a scheduled message for '''
            '''you a week before the time expires, you will be automatically '''
            '''notified and will have time to update.\n\n'''
            '''`@ {2}:  {3}`\n`@ Will off: {4}`\n`@ Telegram Backup {6}`\n\nStay Cool!'''
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

    async def connect(self) -> None:
        await self._TelegramClient.connect()

    async def request_code(self) -> None:
        await self._TelegramClient.send_code_request(self._phone_number)

    async def login(self, password: str=None, code: int=None) -> None:
        if not await self._TelegramClient.is_user_authorized():
            try:
                await self._TelegramClient.sign_in(self._phone_number, code)
            except SessionPasswordNeededError:
                await self._TelegramClient.sign_in(password=password)

    async def request_change_phone_code(self, new_number: str) -> str:
        request = await self._TelegramClient(SendChangePhoneCodeRequest(
            phone_number = new_number,
            settings = CodeSettings(allow_flashcall=True,
                current_number=True
            )
        ))
        return request.phone_code_hash

    async def change_phone(self, code: str, code_hash: str, new_number: str) -> None:
        await self._TelegramClient(ChangePhoneRequest(
            phone_number=new_number, phone_code=code,
            phone_code_hash=code_hash
        ))
    async def backup(self, password: bytes, filename: str=None) -> str:
        tgback_aes = TgbackAES(password)
        tgback_aes.init()

        filename = (filename if filename else str(int(time()))) + '.tgback'

        user = await self._TelegramClient.get_entity('me')
        user = self.__prepare_user_entity(user)

        current_time = time()
        backup_death_at = current_time + 5_356_800

        backup_data = [
            b64encode(tgback_aes._password_hash).decode(),
            self._TelegramClient.session.save(), str(backup_death_at),
            b64encode(user.username.encode()).decode(),
            str(user.id), b64encode(user.last_name.encode()).decode()
        ]
        dump(backup_data, filename)

        await self._TelegramClient.send_file('me',
            open(filename + '.png','rb'),
            caption=self.__notify.format(
                'created', filename, 'Created', ctime(), 
                ctime(backup_death_at),'new ', VERSION
            )
        )
        await self._TelegramClient.send_message('me',
            f'Hello! Please, update your backup `{filename}`. \n\n**One week left!!**',
            schedule=timedelta(seconds=4_752_000)
        )
        return filename

    async def refresh_backup(self, decoded_restored: list, tgback_file_path: str) -> None:
        backup_death_at = time() + 5_356_800

        user = await self._TelegramClient.get_entity('me')
        user = self.__prepare_user_entity(user)

        decoded_restored[2] = backup_death_at
        decoded_restored[3] = user.username
        decoded_restored[4] = user.id
        decoded_restored[5] = user.last_name

        dump(encode_restored(decoded_restored),
            tgback_file_path
        )
        ext = '.png' if not tgback_file_path[-4:] == '.png' else ''
        await self._TelegramClient.send_file('me',
            open(tgback_file_path + ext,'rb'),
            caption=self.__notify.format(
                'updated', tgback_file_path, 'Updated',
                ctime(), ctime(backup_death_at),'', VERSION
            )
        )         
        backup_name = path_split(tgback_file_path)[-1]
        await self._TelegramClient.send_message('me',
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
        decrypted = decrypt_restored(scanqrcode(tgback_file_path), password)
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
    restored = encoded_restored[:]
    restored[0] = b64decode(restored[0])
    restored[1] = restored[1].decode()
    restored[2] = float(restored[2])
    restored[3] = b64decode(restored[3]).decode()
    restored[4] = int(restored[4])
    restored[5] = b64decode(restored[5]).decode()

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
    tgback_aes = TgbackAES('')
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
    while len(encoded) % 100: encoded += b' '
    return make_qr(encoded)

def scanqrcode(qrcode_path: str) -> bytes:
    return b64decode(pyzbar.decode(Image.open(qrcode_path))[0].data.rstrip())
