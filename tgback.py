from os import system as os_system, rename as os_rename
from base64 import b64encode, b64decode
from hashlib import sha512
from time import time

from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, SessionPasswordNeededError
from telethon.tl.functions.account import ChangePhoneRequest, SendChangePhoneCodeRequest
from telethon.tl.types import CodeSettings

from NonCipher import NonCipher, get_hash_of


class TelegramAccount:
    def __init__(self, api_id: int, api_hash: str, phone_number: str):
        self._api_id = api_id
        self._api_hash = api_hash
        self._phone_number = phone_number
        self._session_file = None
        self._TelegramClient = TelegramClient(
            'TelegramBackup', self._api_id, self._api_hash
        )

    async def connect(self):
        await self._TelegramClient.connect()

    async def request_code(self):
        await self._TelegramClient.send_code_request(self._phone_number)

    async def login(self, password: str, code: int):
        if not await self._TelegramClient.is_user_authorized():
            try:
                await self._TelegramClient.sign_in(self._phone_number, code)
            except SessionPasswordNeededError:
                await self._TelegramClient.sign_in(password=password)

    async def change_number(self, new_number: str):
        change_phone_request = await self._TelegramClient(SendChangePhoneCodeRequest(
            phone_number = new_number,
            settings = CodeSettings(allow_flashcall=True, current_number=True)
        ))
        print(change_phone_request.stringify())

    def backup(self, password: str, filename: str=None):
        nc = NonCipher(password, sha512(password.encode()).hexdigest(), 5_000_000)
        nc.init()

        filename = (filename if filename else str(int(time()))) + '.tgback'
        to_backup = '{0} {1}'.format(self._api_id, self._api_hash)

        backup = b64encode(nc.encrypt(to_backup).encode())

        with open(filename,'wb') as f:
            f.write(backup)

        return filename


def restore(tgback_file_path, password):
    nc = NonCipher(password, sha512(password.encode()).hexdigest(), 5_000_000)
    nc.init()

    with open(tgback_file_path,'rb') as f:
        restored = nc.decrypt(b64decode(f.read()))
        return restored.decode().split(' ')


def check_app(api_id, api_hash):
    try:
        TelegramClient('TelegramBackup', api_id, api_hash)
        return True
    except: return False
