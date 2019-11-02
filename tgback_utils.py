from sqlite3 import connect as sqlite3_connect
from base64 import b64encode, b64decode
from hashlib import md5, sha512
from shutil import copyfile
from ast import literal_eval
from time import time

from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, SessionPasswordNeededError
from telethon.tl.functions.account import ChangePhoneRequest, SendChangePhoneCodeRequest
from telethon.tl.types import CodeSettings
from telethon.sessions.abstract import Session

from NonCipher import NonCipher, get_hash_of


class TelegramAccount:
    def __init__(self, api_id: int, api_hash: str, phone_number: str):
        self._api_id = api_id
        self._api_hash = api_hash
        self._phone_number = phone_number
        self._session_filename = 'tgback_' + md5(str(api_id).encode()).hexdigest() + '.session'
        self._TelegramClient = TelegramClient(
            self._session_filename,
            self._api_id, self._api_hash
        )
    async def connect(self):
        await self._TelegramClient.connect()

    def remove_session(self):
        try:
            self._TelegramClient.session._conn.commit()
            self._TelegramClient.session.close()
            self._TelegramClient.session.delete()
        except:
            return False
        return True

    async def request_code(self):
        await self._TelegramClient.send_code_request(self._phone_number)

    async def login(self, password: str=None, code: int=None):
        if not await self._TelegramClient.is_user_authorized():
            try:
                await self._TelegramClient.sign_in(self._phone_number, code)
            except SessionPasswordNeededError:
                await self._TelegramClient.sign_in(password=password)

    async def request_change_phone_code(self, new_number: str):
        request = change_phone_request = await self._TelegramClient(SendChangePhoneCodeRequest(
            phone_number = new_number,
            settings = CodeSettings(allow_flashcall=True, current_number=True)
        ))
        return request.phone_code_hash

    async def change_phone(self, code: str, code_hash: str, new_number: str):
        await self._TelegramClient(ChangePhoneRequest(
            phone_number=new_number, phone_code=code,
            phone_code_hash=code_hash
        ))

    def backup(self, password: str , filename: str=None):
        nc = NonCipher(password, sha512(password.encode()).hexdigest(), 5_000_000)
        nc.init()

        filename = (filename if filename else str(int(time()))) + '.tgback'

        session_db = sqlite3_connect(self._session_filename)
        session_cursor = session_db.cursor()

        metadata = session_cursor.execute('SELECT * FROM sessions')
        metadata = metadata.fetchall()
        session_db.close()

        to_backup = (self._phone_number,
            (self._api_id, self._api_hash), metadata[0]
        )
        backup = b64encode(nc.encrypt(repr(to_backup)).encode())

        with open(filename,'wb') as f:
            f.write(backup)

        return filename


def restore(tgback_file_path: str, password: str):
    nc = NonCipher(password, sha512(password.encode()).hexdigest(), 5_000_000)
    nc.init()

    with open(tgback_file_path,'rb') as f:
        restored = nc.decrypt(b64decode(f.read()))
        return (literal_eval(restored.decode()), (nc._primary_hash, nc._hash_of_input_data))


def make_session(restored_backup: tuple):
    session_filename = 'tgback_' + md5(
        str(restored_backup[1][0]).encode()
    ).hexdigest() + '.session'

    copyfile('template.tsession', session_filename)

    session_db = sqlite3_connect(session_filename)
    session_cursor = session_db.cursor()

    session_cursor.execute(
        'INSERT INTO sessions VALUES (?,?,?,?,?)',
        restored_backup[2]
    )
    session_db.commit()
    session_db.close()
