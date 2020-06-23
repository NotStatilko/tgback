print('\n' * 35 + '@ TelegramBackup is loading...')

import os.path

from getpass import getpass
from traceback import print_exc
from time import ctime, strftime
from reedsolo import ReedSolomonError
from PIL import UnidentifiedImageError
from asyncio import run as asyncio_run
from os import system as os_system, cpu_count

from telethon.errors.rpcerrorlist import (
    AuthKeyUnregisteredError, PhoneCodeInvalidError,
    PasswordHashInvalidError, PhoneNumberOccupiedError,
    PhoneNumberInvalidError, FloodWaitError, PhoneCodeEmptyError,
    PhoneCodeInvalidError, FreshChangePhoneForbiddenError
)
from tgback_utils import TelegramAccount, restore, VERSION


if cpu_count() > 1:
    from time import time
    from hashlib import sha3_256

    hashing_time_start = time()
    to_hash = b'0' * 32
    for i in range(1000):
        sha3_256(to_hash).digest()

    HASHING_TIME = f'~{round(2_222.222 * (time() - hashing_time_start))}s'
else:
    HASHING_TIME = 'some time'

def clear_terminal():
    os_system('cls || clear')
    print('\n' * 35)

async def main():
    try:
        async def request_confirmation_code(request_coroutine, phone, rcpc=False) -> tuple:
            while True:
                clear_terminal()
                print('@ Requesting confirmation code...')

                if rcpc:
                    code_hash = await request_coroutine(phone)
                else:
                    code_hash = await request_coroutine()

                # code_hash is for request_change_phone_code (rcpc)

                clear_terminal()

                print(f'@ Please wait for message or call with code ({phone})')
                print(f'@ Last request sended at {strftime("%H:%M:%S")}\n')
                print('> 1) I received the code')
                print('>> 2) I haven\'t recieved code')
                print('>>> 3) Return to main page')
                mode = input('\n@ Input: ')

                if mode == '1':
                    clear_terminal()
                    code = input('> Confirmation Code: ')
                    break

                elif mode == '3':
                    await main()

            clear_terminal()
            return (code, code_hash)

        while True:
            clear_terminal()
            print(
                f''' - TelegramBackup {VERSION} -\n\n'''
                '''> 1) Backup Telegram account\n'''
                '''>> 2) Open .tgback backup\n'''
                '''>>> 3) Exit from TelegramBackup'''
                '''\n\n% Press Ctrl+C to back here'''
            )
            selected_section = input('\n@ Input: ')
            if selected_section and selected_section in '123':
                break

        return_to_main = False
        while True:
            if return_to_main:
                await main()

            clear_terminal()
            if selected_section == '1':
                while True:
                    clear_terminal()
                    print(
                        '''> 1) Manual input\n'''
                        '''>> 2) Load config file\n'''
                        '''>>> 3) Return to main page\n'''
                    )
                    selected_section = input('@ Input: ')
                    if selected_section == '1':
                        clear_terminal()
                        phone = input('> Phone number: ')
                        try:
                            clear_terminal()
                            print('@ Checking number for correctness...')
                            account = TelegramAccount(phone)
                            await account.connect()

                            code, _ = await request_confirmation_code(
                                account.request_code, phone
                            )
                            password = getpass('>> Your Telegram password: ')
                            clear_terminal()
                            try:
                                print('@ Trying to connect with Telegram...')
                                await account.login(password,code)


                                while True:
                                    clear_terminal()
                                    tgback_filename = input('> Backup filename: ')
                                    if tgback_filename > 32:
                                        input('@: ! Backup filename is too long! (Must be < 33).')
                                        tgback_filename = input('> Backup filename: ')
                                    else:
                                        break

                                tgback_password = getpass('>> Backup password: ')
                                c_tgback_password = getpass('>>> Re-enter password: ')
                                while True:
                                    if tgback_password != c_tgback_password:
                                        clear_terminal()
                                        print('@: ! Password mismatch! Try again.\n')
                                        tgback_password = getpass('> Backup password: ')
                                        c_tgback_password = getpass('>> Re-enter password: ')
                                    else:
                                        break

                                clear_terminal()
                                print(f'@ Password is hashing, please wait {HASHING_TIME}...')

                                filename = await account.backup(tgback_password, tgback_filename)

                                clear_terminal()
                                input(f'@ Successfully encrypted and backuped! ({filename})')
                                await main()

                            except (KeyboardInterrupt, EOFError):
                                await main()

                            except PhoneCodeInvalidError:
                                clear_terminal()
                                input('\n@: ! Code you entered is invalid. Try again.')

                            except PasswordHashInvalidError:
                                clear_terminal()
                                input('\n@: ! Password you entered is invalid. Try again.')

                        except FloodWaitError as e:
                            clear_terminal()
                            input('''@: ! Telegram servers returned FloodWaitError. '''
                                f'''Please wait {e.seconds} seconds ''')
                            await main()

                        except KeyboardInterrupt:
                            await main()

                        except PhoneNumberInvalidError:
                            clear_terminal()
                            input(f'@: ! The provided number ({phone}) is invalid')
                            await main()

                    elif selected_section == '2': # Config file
                        clear_terminal()
                        config = input('> Path to tgback-config file: ')
                        if not os.path.exists(config):
                            clear_terminal()
                            input('@: ! Can\'t open config file. Check your path. ')
                        else:
                            config_template = (
                                '''phone_number; telegram_password; '''
                                '''backup_password; backup_filename'''
                            )
                            try:
                                config = open(config).read()

                                # Invalid format but ok. I try to predict it :)
                                config = config.replace('"','')
                                config = config.replace(' ','')
                                config = config.replace('\n','')

                                config = config.split(';')
                                config = config[:4] if not config[-1] else config
                                assert len(config) == 4

                                if not config[3]:
                                    config[3] = str(int(time()))

                                if len(config[3]) > 32:
                                    raise TypeError

                            except AssertionError:
                                clear_terminal()
                                input(
                                     '''@: ! It\'s not a tgback-config file\n\n'''
                                    f'''@: ? Correct format: "{config_template}"\n\n'''
                                     '''@: ? Use manual input if your password contain ";".'''
                                )
                                await main()
                            except TypeError:
                                clear_terminal()
                                input('@: ! Backup filename is too long! (Must be < 33).')
                                await main()
                            try:
                                clear_terminal()
                                print('@ Trying to connect with Telegram...')
                                account = TelegramAccount(phone_number=config[0])
                                await account.connect()
                                try:
                                    code, _ = await request_confirmation_code(
                                        account.request_code, config[0]
                                    )
                                    clear_terminal()
                                    print('@ Trying to login...')
                                    await account.login(config[1],code)
                                    clear_terminal()

                                except PhoneCodeInvalidError:
                                    clear_terminal()
                                    input('@: ! Invalid code. Try again. ')
                                    await main()
                                except PasswordHashInvalidError:
                                    clear_terminal()
                                    input('@: ! Invalid password. Try again. ')
                                    await main()
                                else:
                                    print(f'@ Password is hashing, please wait {HASHING_TIME}...')

                                    filename = await account.backup(config[2],config[3])
                                    #decoded_backup = reedsolo_decode(open(filename,'rb').read())
                                    #makeqrcode(decoded_backup).save(filename + '.png')

                                    clear_terminal()
                                    input(f'@ Successfully encrypted and backuped! ({filename})')

                                    return_to_main = True; break

                            except ConnectionError:
                                clear_terminal()
                                input('@: ! Unable to connect with Telegram servers. Check your internet connection.')
                                await main()
                            except:
                                clear_terminal()
                                input(
                                     '''@: ! Something wrong in your config file.\n\n'''
                                    f'''@: ? Correct format: "{config_template}"\n\n'''
                                     '''@: ? If your password contain ";", please, use manual input.'''
                                )
                    elif selected_section == '3':
                        await main()

            elif selected_section == '2': # Open .tgback
                while True:
                    clear_terminal()
                    print('> 1) Load from QR')
                    print('>> 2) Use .tgback file')
                    print('>>> 3) Back to main page')

                    open_mode = input('\n@ Input: ')

                    if open_mode and open_mode in '123':
                        clear_terminal(); break

                if open_mode == '3':
                    await main()

                backup_type = 'QR' if open_mode == '1' else 'file'
                is_qr = True if open_mode == '1' else False
                path_to_tgback = input(f'> Path to .tgback {backup_type}: ')

                if not os.path.exists(path_to_tgback):
                    clear_terminal()
                    input(f'@: ! Can\'t find .tgback {backup_type}. Check entered path.')
                    await main()
                else:
                    tgback_password = getpass(f'>> Password to .tgback {backup_type}: ')
                    clear_terminal()
                    print(f'@ Password is hashing, please wait {HASHING_TIME}...')
                    try:
                        restored = restore(path_to_tgback, tgback_password, is_qr=is_qr)
                        assert len(restored) == 6
                    except (AssertionError, ValueError, ReedSolomonError):
                        clear_terminal()
                        input('\n@: ! Incorrect Password or corrupted backup. ')
                        await main()
                    except (IndexError, UnidentifiedImageError):
                        clear_terminal()
                        input('''\n@: ! Impossible to read QR code. '''
                              '''Are you sure that image is correct and in good quality?''')
                        await main()
                    else:
                        account = TelegramAccount(session=restored[1])
                        await account.connect()

                        while True:
                            clear_terminal()
                            return_to_page = False
                            print(
                                f'''% Hello, {restored[3] + ' ' + restored[5]}! (id{restored[4]})\n'''
                                f'''@ Backup valid until {ctime(float(restored[2]))}\n\n'''
                                f'''> 1) Change account phone number\n'''
                                f'''>> 2) Refresh .tgback backup\n'''
                                f'''>>> 3) Return to main page'''
                            )
                            selected_section = input('\n@ Input: ')
                            if selected_section == '1':
                                clear_terminal()
                                while True:
                                    if return_to_page:
                                        break
                                    clear_terminal()
                                    new_phone = input('> Enter your new phone number: ')
                                    try:
                                       code, code_hash = await request_confirmation_code(
                                           account.request_change_phone_code, new_phone, rcpc=True,
                                       )
                                       await account.change_phone(code, code_hash, new_phone)

                                    except FreshChangePhoneForbiddenError:
                                        return_to_page = True
                                        clear_terminal()
                                        input('\n@: ! Can\'t change phone number now. Please, wait some time.')
                                        break

                                    except PhoneCodeInvalidError:
                                        clear_terminal()
                                        return_to_page = True
                                        input('@: ! The code you entered is invalid. Try again.')

                                    except AuthKeyUnregisteredError:
                                        clear_terminal()
                                        return_to_page = True
                                        input('\n@: ! Backup was disconnected.'); break

                                    except PhoneNumberOccupiedError:
                                        clear_terminal()
                                        return_to_page = True
                                        input(f'\n@: ! Number {new_phone} already in use. ')

                                    except PhoneNumberInvalidError:
                                        clear_terminal()
                                        return_to_page = True
                                        input(f'\n@: ! Number {new_phone} is invalid. ')

                                    except FloodWaitError as e:
                                        clear_terminal()
                                        input('''@: ! Telegram servers returned FloodWaitError. '''
                                            f'''Please wait {e.seconds} seconds ''')
                                        return_to_page = True
                                    else:
                                        break

                                if not return_to_page:
                                    clear_terminal()
                                    input('''@: Your phone has been successfully changed! '''
                                         f'''Now you can login to your Telegram account with phone {new_phone}!''')
                                    await main()

                            elif selected_section == '2':
                                try:
                                    clear_terminal()
                                    print('@ Refreshing...')
                                    await account.refresh_backup(restored, path_to_tgback)
                                except:
                                    clear_terminal()
                                    input('\n\n@: ! Backup was disconnected.')

                            elif selected_section == '3':
                                await main()

            elif selected_section == '3':
                raise SystemExit
            else:
                await main()

    except (KeyboardInterrupt, EOFError):
        await main()

    except SystemExit:
        raise SystemExit

    except ConnectionError:
        clear_terminal()
        input('@: ! Unable to connect with Telegram servers. Check your internet connection.')
        await main()

    except Exception as e:
        clear_terminal()
        print_exc(file=open('tgback.log','a'))
        print(
            f'''@: ! Oops, something went wrong! Unknown error was '''
            '''written to the "tgback.log" file, so please, '''
            '''send it to me on Telegram (t.me/not_statilko), '''
            '''or open issue on GitHub (bit.ly/tgback). '''
            '''I will fix it as soon as possible. Thanks in advance!\n\n'''
            f'''Short error: {e}\n'''
        )
        input('@ Press Enter to return')
        await main()


asyncio_run(main())
