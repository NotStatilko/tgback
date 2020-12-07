print('\n' * 100 + '@ TelegramBackup is loading...')

import os.path

from tgback_utils import (
    TelegramAccount, TgbackAES, restore,
    VERSION, qr_available, image_error, scanqrcode
)
from getpass import getpass
from sys import platform
from traceback import print_exc
from time import ctime, strftime

from reedsolo import ReedSolomonError

from asyncio import run as asyncio_run
from os import system as os_system, cpu_count

from telethon.errors.rpcerrorlist import (
    AuthKeyUnregisteredError, PhoneCodeInvalidError,
    PasswordHashInvalidError, PhoneNumberOccupiedError,
    PhoneNumberInvalidError, FloodWaitError, PhoneCodeEmptyError,
    PhoneCodeInvalidError, FreshChangePhoneForbiddenError
)
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
    os_system("printf '\33c\e[3J'")
    print('\n' * 100)

async def main():
    try:
        async def request_confirmation_code(request_coroutine, phone: str, account: TelegramAccount=None) -> tuple:
            request_code = True
            code_hash = None
            while True:
                clear_terminal()
                if request_code:
                    print('@ Requesting confirmation code...')

                    if account: # if account specified then it's request to change phone
                        if not code_hash:
                            code_hash = await request_coroutine(phone)
                          # code_hash is for request_change_phone_code
                        else:
                            await account.resend_code(phone, code_hash)
                    else:
                        code_hash = await request_coroutine()

                    request_time = f'{strftime("%I:%M:%S %p")}'
                    clear_terminal()

                print(f'@ Please wait for message or call with code ({phone})')
                print(f'@ Last request sended at {request_time}\n')
                print('> 1) I received the code')
                print('>> 2) I haven\'t recieved code')
                print('>>> 3) Return to main page')
                mode = input('\n@ Input: ')

                if mode == '1':
                    clear_terminal()
                    code = input('> Confirmation Code: ')
                    break

                elif mode == '2':
                    request_code = True

                elif mode == '3':
                    await main()

                else:
                    request_code = False

            clear_terminal()
            return (code, code_hash)

        while True:
            clear_terminal()
            about_qr = '' if qr_available else '(not available)'
            print(
                f''' - TelegramBackup {VERSION} (bit.ly/tgback) -\n\n'''
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
                                    if len(tgback_filename) > 32:
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
                                input(f'@ Successfully encrypted and backuped! ("{filename})"')
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

                        except (PhoneNumberInvalidError, TypeError):
                            clear_terminal()
                            input(f'@: ! The provided number ("{phone}") is invalid. Try again.')
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

                                    clear_terminal()
                                    input(f'@ Successfully encrypted and backuped! ("{filename})"')

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
                    print('> 1) Load from QR ' + about_qr)
                    print('>> 2) Use .tgback file')
                    print('>>> 3) Back to main page')

                    open_mode = input('\n@ Input: ')

                    if open_mode == '1' and not qr_available:
                        clear_terminal()
                        input('@: ! Can\'t reach ZBar or PIL. Please check installed dependecies. ')
                        await main()


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
                    except (IndexError, image_error):
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
                            about_qr = '' if qr_available else '(not available)'
                            print(
                                f'''% Hello, {restored[3] + ' ' + restored[5]}! (id{restored[4]})\n'''
                                f'''@ Backup valid until {ctime(float(restored[2]))}\n\n'''
                                '''> 1) Change account phone number\n'''
                                '''>> 2) Refresh .tgback backup\n'''
                                f'''>>> 3) Log in to TelegramDesktop {about_qr}\n'''
                                '''>>>> 4) Change backup password\n'''
                                '''>>>>> 5) Destroy backup\n'''
                                '''>>>>>> 6) Return to main page'''
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
                                           account.request_change_phone_code, new_phone, account=account,
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

                            elif selected_section == '3' and not qr_available:
                                clear_terminal()
                                input('@: ! Can\'t reach ZBar or PIL. Please check installed dependecies. ')

                            elif selected_section == '3':
                                while True:
                                    clear_terminal()
                                    print(
                                        '''% Please open TelegramDesktop and choose "Login via QR" option.\n'''
                                        '''  If you already logged in then tap burger icon and "Add Account".\n'''
                                        '''  Screenshot QR code that Telegram showed you and enter path to image.\n'''
                                        '''  Telegram refreshes this QR every 30 seconds, so do it quick!\n\n'''
                                        '''> 1) Okay, i already screenshoted QR\n>> 2) Go back\n'''
                                    )
                                    choice = input('@ Input: ')
                                    clear_terminal()
                                    if choice == '1':
                                        qrcode_path = input('@ Telegram QR path: ')
                                        clear_terminal()
                                        if os.path.exists(qrcode_path):
                                            try:
                                                print('Scanning Telegram auth QR code...')
                                                token = scanqrcode(qrcode_path).split(b'token=')[1]
                                                await account.accept_login_token(token)
                                                clear_terminal()
                                                input('@: Successfully logged in! ')
                                                break
                                            except:
                                                input('''@: ! Can\'t log in. Please check your screenshot, try to increase '''
                                                      '''size of QR or wait 30 seconds and screenshot new QR code. ''')
                                        else:
                                            input(
                                                '''@: ! Sorry, i can\'t open path that you provided. '''
                                                '''Re-screenshot new QR and check your path.'''
                                            )
                                    elif choice == '2':
                                        break

                            elif selected_section == '4':
                                clear_terminal()
                                new_password = getpass('> Your new password: ')
                                c_new_password = getpass('>> Confirm password: ')
                                if new_password != c_new_password:
                                    clear_terminal()
                                    input('@: ! Password mismatch. Please try again.')
                                else:
                                    clear_terminal()
                                    print(f'@ Password is hashing, please wait {HASHING_TIME}...')
                                    restored[0] = TgbackAES(b'')._hash_password(new_password.encode()).digest()
                                    clear_terminal()
                                    print('@ Refreshing...')
                                    await account.refresh_backup(restored, path_to_tgback)
                                    clear_terminal()
                                    input('@: Your password has been successfully changed! ')

                            elif selected_section == '5':
                                while True:
                                    clear_terminal()
                                    print(
                                        '''% Are you sure you want to destroy your backup?\n\n'''
                                        '''> 1) Yes\n>> 2) No\n'''
                                    )
                                    confirm = input('@ Input: ')
                                    if confirm == '1':
                                        clear_terminal()
                                        print('''% No, seriously. After this operation, you will no longer be '''
                                            '''able to change your phone number through this backup.\n''')
                                        print('% Are you totally sure? Type "yes" or "no"\n')
                                        if input('@ Input: ') == 'yes':
                                            clear_terminal()
                                            if await account.logout():
                                                input('@: Successfully. Now you can delete your backup file.')
                                                await main()
                                            else:
                                                input('@: ! Something went wrong, can\'t disconnect session. Try again.')
                                                break
                                        else:
                                            break

                                    elif confirm == '2':
                                        break

                            elif selected_section == '6':
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
