from time import time, ctime
from datetime import timedelta

from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, SessionPasswordNeededError
from telethon.tl.functions.account import ChangePhoneRequest, SendChangePhoneCodeRequest
from telethon.tl.types import CodeSettings
from telethon.sessions import StringSession

from os.path import split as path_split
from hashlib import md5, sha1, sha512, sha3_256
from pyaes import AESModeOfOperationCBC, Encrypter, Decrypter
from pyaes.util import append_PKCS7_padding, strip_PKCS7_padding


class TgbackAES:
    def __init__(self, password: bytes):        
        if not isinstance(password, bytes):
            password = password.encode()
            
        self.__raw_password = password        
        self.__password_hash = None; self.__iv = None
    
    @staticmethod
    def _hash_password(password: bytes, iter_count=2_222_222) -> sha3_256:        
        init = sha512(sha1(md5(password).digest()).digest())
        init = sha512(sha3_256(md5(init.digest()).digest()).digest())
        
        for _ in range(iter_count):
            init = sha3_256(init.digest())
        
        return init
    
    def init(self, password_hash: bytes=None) -> None:               
        if password_hash:
            self._password_hash = password_hash
        else:
            if not self.__raw_password:
                raise Exception('Already initialized')
            else:                
                self._password_hash = self._hash_password(self.__raw_password).digest()                  
                self.__raw_password = None
        
        self.__iv = sha512(self._password_hash).digest()[:16] 
        
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
            encrypted = aes_cbc.feed(data)
            encrypted += aes_cbc.feed()           
            return encrypted
    
    def decrypt(self, edata: bytes) -> bytes:
        if not self._password_hash:
            raise Exception('You need to call .init() for first')
                        
        elif not isinstance(edata, bytes):
            raise Exception('edata must be bytes')            
        else:
            aes_cbc = Decrypter(
                AESModeOfOperationCBC(
                    self._password_hash, self.__iv)
            )
            decrypted = aes_cbc.feed(edata)
            decrypted += aes_cbc.feed()
            return strip_PKCS7_padding(decrypted)


class TelegramAccount:
    def __init__(self, api_id: int, api_hash: str, phone_number: str=None, session: str=None):
        self._api_id = int(api_id)
        self._api_hash = api_hash
        self._phone_number = phone_number       
        self._TelegramClient = TelegramClient(
            StringSession(session), self._api_id, self._api_hash
        )
        self.__notify = (
            """Your {5}backup has been {0}!\n\nRemember that """
            """**every two months** it needs to be updated, otherwise you will """
            """**lose access** to `{1}`. I created a delayed message for """
            """you a week before the time expires, you will be automatically """
            """notified and will have time to update.\n\n"""
            """`@ {2}:  {3}`\n`@ Will off: {4}`\n\nStay Cool!"""        
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
            settings = CodeSettings(allow_flashcall=True, current_number=True)
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

        filename = (filename if filename else str(int(time()))) + '.etgback'        
        
        user = await self._TelegramClient.get_entity('me')        
        user = self.__prepare_user_entity(user)
        
        current_time = time()
        backup_death_at = current_time + 5_356_800
        
        backup_data =  f'{self._api_id}<*>{self._api_hash}<*>'
        backup_data += f'{tgback_aes._password_hash.hex()}<*>'
        backup_data += self._TelegramClient.session.save()
        backup_data += f'<*>{backup_death_at}<*>{user.username}<*>{user.id}'
        backup_data += f'<*>{user.last_name}'
                                                      
        await self._TelegramClient.send_message('me',self.__notify.format(
            'created', filename, 'Created', ctime(), ctime(backup_death_at),'new ')
        )
        await self._TelegramClient.send_message('me',
            f'Hello! Please, update your backup `{filename}`. \n\n**One week left!!**',
            schedule=timedelta(seconds=4_752_000)
        )
        with open(filename,'w') as f:
            f.write(tgback_aes.encrypt(backup_data).hex())

        return filename
    
    async def refresh_backup(self, restored: list, tgback_file_path: str) -> None:        
        backup_death_at = time() + 5_356_800
        
        user = await self._TelegramClient.get_entity('me')
        user = self.__prepare_user_entity(user)
        
        restored[4] = backup_death_at
        restored[5] = user.username
        restored[6] = user.id
        restored[7] = user.last_name
        
        dump(restored, tgback_file_path)
        
        await self._TelegramClient.send_message('me',self.__notify.format(
            'updated', tgback_file_path, 'Updated', 
            ctime(), ctime(backup_death_at),'')
        )
        backup_name = path_split(tgback_file_path)[-1]
        await self._TelegramClient.send_message('me',
            f'Hello! Please, update your backup `{backup_name}`\n\n**One week left!!**',
            schedule=timedelta(seconds=4_752_000)
        )

def restore(tgback_file_path: str, password: bytes) -> list:
    tgback_aes = TgbackAES(password)
    tgback_aes.init()
        
    with open(tgback_file_path,'rt') as f:       
        return tgback_aes.decrypt(
            bytes(bytearray.fromhex(f.read()))
        ).decode().split('<*>')


def dump(restored: list, tgback_file_path: str):    
    tgback_aes = TgbackAES('')
    tgback_aes.init(bytearray.fromhex(restored[2]))   
       
    with open(tgback_file_path,'w') as f:
        restored_str = (str(i) for i in restored)
        f.write(tgback_aes.encrypt('<*>'.join(restored_str)).hex())