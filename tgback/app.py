#!/usr/bin/python3

print('\n' * 100 + '@ TGBACK is loading...')

from pathlib import Path
from sys import platform

from getpass import getpass
from traceback import print_exc
from os import system as os_system

from datetime import datetime
from time import ctime, strftime, sleep

from code import interact as interactive_console
from pickle import UnpicklingError

from telethon.errors.rpcerrorlist import (
    AuthKeyUnregisteredError, PhoneCodeInvalidError,
    PasswordHashInvalidError, PhoneNumberOccupiedError,
    PhoneCodeInvalidError, FreshChangePhoneForbiddenError,
    PhoneNumberInvalidError, FloodWaitError, PhoneCodeEmptyError
)
from telethon.tl.functions.contacts import (
    ImportContactsRequest, DeleteContactsRequest
)
from telethon.tl.types import InputPhoneContact
from telethon.utils import logging

from .tools import (
    QR_ERROR, scanqrcode, restore,
    QR_AVAILABLE, ABSPATH,
    TelegramAccount, make_scrypt_key
)
from .version import VERSION


# We really don't need this here
logging.disable()

if platform.startswith('win'):
    clear_command = 'cls'
elif platform.startswith('cygwin'):
    clear_command = 'printf "\033c"'
else:
    clear_command = "printf '\33c\e[3J' || cls || clear"

def clsprint(*args, **kwargs):
    os_system(clear_command)
    print('\n' * 100)
    print(*args, **kwargs)

class FlushToStartPage(Exception):
    """
    Will be used as navigation flag.
    Raised -> return to start page.
    """

class ExitApp(Exception):
    """Will be raised when user want to exit app"""

def app():
    def request_confirmation_code(
            request_func, phone: str,
            account: TelegramAccount=None) -> tuple:

        request_code, code_hash = True, None
        phone = phone.replace(' ','')

        while True:
            if request_code:
                clsprint('@ Requesting confirmation code...')

                if account: # if account specified then it's request to change phone
                    if not code_hash:
                        code_hash = request_func(phone)
                      # code_hash is for request_change_phone_code
                    else:
                        account.resend_code(phone, code_hash)
                else:
                    code_hash = request_func()

                request_time = f'{strftime("%I:%M:%S %p")}'

            clsprint(
               f'''@ Please wait for message or call with code ({phone})\n'''
               f'''@ Last request was sended at {request_time}\n\n'''

                '''> 1) I received the code\n'''
                '''>> 2) I haven\'t recieved code\n'''
                '''>>> 3) Return to main page\n'''
            )
            mode = input('@ Input: ')

            if mode == '1':
                clsprint()
                code = input('> Confirmation Code: ')
                break

            elif mode == '2':
                request_code = True

            elif mode == '3':
                raise FlushToStartPage

            else:
                request_code = False

        return (code, code_hash)

    while True:
        about_qr = '' if QR_AVAILABLE else '(not available)'

        clsprint(
           f''' - TGBACK v{VERSION} (bit.ly/tgback) -\n\n'''

            '''> 0) Quick help & What It Is?\n'''
            '''>> 1) Backup Telegram account\n'''
            '''>>> 2) Open TGBACK backup file\n'''
            '''>>>> 3) Exit from TelegramBackup'''

            '''\n\n% Press Ctrl+C to back here'''
        )
        selected_section = input('\n@ Input: ')

        if selected_section and selected_section in '0123P':
            break

    while True:
        if selected_section == 'P':
            clsprint()
            print('@ !!! WARNING !!! DO NOT EXECUTE CODE YOU DON\'T TRUST !!!\n')
            interactive_console(local=globals())
            raise FlushToStartPage

        if selected_section == '0':
            help_text = open(ABSPATH / 'data' / 'help.txt')
            clsprint(help_text.read())
            input('\n@ Press Enter to return ')

        if selected_section == '1':
            while True:
                clsprint(
                    '''> 1) Manual input\n'''
                    '''>> 2) Load config file\n'''
                    '''>>> 3) Return to main page\n'''
                )
                selected_section = input('@ Input: ')
                if selected_section == '1':
                    clsprint()
                    phone = input('> Phone number: ')
                    try:
                        clsprint('@ Checking number for correctness...')
                        account = TelegramAccount(phone)
                        account.connect()

                        code, _ = request_confirmation_code(
                            account.request_code, phone
                        )
                        password = getpass('>> Your Telegram password (hidden): ')
                        try:
                            clsprint('@ Trying to connect with Telegram...')
                            account.login(password,code)

                            while True:
                                clsprint()
                                tgback_filename = input('> Backup filename: ')
                                if len(tgback_filename) > 32:
                                    input('@: ! Backup filename is too long! (Must be < 33).')
                                    tgback_filename = input('> Backup filename: ')
                                else:
                                    break

                            while True:
                                clsprint('@ To create backup you need at least 1GB free of RAM.\n')
                                tgback_password = getpass('> Backup password (hidden): ')
                                c_tgback_password = getpass('>> Re-enter password (hidden): ')

                                if tgback_password != c_tgback_password:
                                    clsprint()
                                    input('@: ! Password mismatch! Try again.\n')
                                elif not tgback_password:
                                    clsprint()
                                    input('@: ! Password can\'t be empty.\n')
                                else:
                                    break

                            clsprint('@ Creating key & making backup...')

                            backup = account.backup(
                                tgback_password.encode(),
                                tgback_filename
                            )
                            clsprint()
                            input(f'@ Successfully encrypted and backuped! ({backup[0]})')
                            raise FlushToStartPage

                        except (KeyboardInterrupt, EOFError):
                            raise FlushToStartPage

                        except PhoneCodeInvalidError:
                            clsprint()
                            input('\n@: ! Code you entered is invalid. Try again.')

                        except PasswordHashInvalidError:
                            clsprint()
                            input('\n@: ! Password you entered is invalid. Try again.')

                    except FloodWaitError as e:
                        clsprint()
                        input(
                            '''@: ! Telegram servers returned FloodWaitError.\n'''
                           f'''     Please wait {e.seconds} seconds ''')
                        raise FlushToStartPage

                    except KeyboardInterrupt:
                        raise FlushToStartPage

                    except (PhoneNumberInvalidError, TypeError):
                        clsprint()
                        input(f'@: ! The provided number ({phone}) is invalid.')
                        raise FlushToStartPage

                elif selected_section == '2': # Config file
                    clsprint()
                    config = input('> Path to tgback-config file: ')

                    if not Path(config).exists():
                        clsprint()
                        input('@: ! Can\'t open config file. Check your path. ')

                    elif Path(config).is_dir():
                        clsprint()
                        input('@: ! Specified path is a directory, not a file. ')
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
                            clsprint()
                            input(
                                 '''@: ! It\'s not a tgback-config file\n\n'''
                                f'''@: ? Correct format: "{config_template}"\n\n'''
                                 '''@: ? Use manual input if your password contains ";" symbol.\n'''
                            )
                            raise FlushToStartPage
                        except TypeError:
                            clsprint()
                            input('@: ! Backup filename is too long! (Must be < 33).')
                            raise FlushToStartPage
                        try:
                            clsprint('@ Trying to connect with Telegram...')
                            account = TelegramAccount(phone_number=config[0])
                            account.connect()
                            try:
                                code, _ = request_confirmation_code(
                                    account.request_code, config[0]
                                )
                                clsprint('@ Trying to login...')
                                account.login(config[1],code)

                            except PhoneCodeInvalidError:
                                clsprint()
                                input('@: ! Invalid code. Try again. ')
                                raise FlushToStartPage

                            except PasswordHashInvalidError:
                                clsprint()
                                input('@: ! Invalid password. Try again. ')
                                raise FlushToStartPage

                            else:
                                clsprint('@ Creating key & making backup...')
                                backup = account.backup(config[2].encode(), config[3])

                                clsprint()
                                input(f'@ Successfully encrypted and backuped! ({backup[0]})')

                                raise FlushToStartPage

                        except ConnectionError:
                            raise ConnectionError
                        except:
                            clsprint()
                            input(
                                 '''@: ! Something wrong in your config file.\n\n'''
                                f'''@: ? Correct format: "{config_template}"\n\n'''
                                 '''@: ? If your password contain ";", please, use manual input.\n'''
                            )
                elif selected_section == '3':
                    raise FlushToStartPage

        elif selected_section == '2': # Open .tgback
            while True:
                clsprint(
                   f'''> 1) Load from QR {about_qr}\n'''
                    '''>> 2) Use .tgback file\n'''
                    '''>>> 3) Back to main page\n'''
                )
                open_mode = input('@ Input: ')

                if open_mode == '1' and not QR_AVAILABLE:
                    clsprint()
                    input('@: ! Can\'t reach ZBar or PIL. Please check installed dependecies. ')
                    raise FlushToStartPage

                if open_mode and open_mode in '123':
                    clsprint(); break

            if open_mode == '3':
                raise FlushToStartPage

            backup_type = 'QR' if open_mode == '1' else 'file'
            is_qr = True if open_mode == '1' else False
            path_to_tgback = input(f'> Path to .tgback {backup_type}: ')

            if not Path(path_to_tgback).exists():
                clsprint()
                input(f'@: ! Can\'t find .tgback {backup_type}. Check entered path.')
                raise FlushToStartPage

            elif Path(path_to_tgback).is_dir():
                clsprint()
                input('@: ! Specified path is a directory, not a file. ')
                raise FlushToStartPage
            else:
                while True:
                    clsprint('@ To decrypt backup you need at least 1GB free of RAM.\n')
                    tgback_password = getpass(f'>> Password to .tgback {backup_type} (hidden): ')
                    if not tgback_password:
                        clsprint()
                        input('@: ! Password can\'t be empty. Try again or press Ctrl+C.')
                    else:
                        break

                clsprint('@ Creating key with your password...')
                try:
                    restored = restore(path_to_tgback, tgback_password.encode(), is_qr=is_qr)
                except (IndexError, QR_ERROR):
                    clsprint()
                    input(
                        '''\n@: ! Can't read QR code you specified.\n'''
                        '''     Are you sure that image is QR and good quality?\n'''
                    )
                    raise FlushToStartPage
                except:
                    clsprint()
                    input('\n@: ! Incorrect password or corrupted backup. ')
                    raise FlushToStartPage
                else:
                    try:
                        account = TelegramAccount(session=restored['session'])
                        account.connect()

                        user = account.TelegramClient.get_me()
                        name = f'@{user.username}' if user.username else user.first_name
                    except AttributeError:
                        clsprint()
                        input('@: ! Backup was disconnected. ')
                        raise FlushToStartPage

                    while True:
                        return_to_page = False

                        clsprint(
                            f'''% Hello, {name}! (+{user.phone})\n'''
                            f'''@ Backup valid until {ctime(restored['death_at'])}\n\n'''

                            '''> 1) Change phone number of account\n'''
                            '''>> 2) Refresh .tgback backup session\n'''
                            '''>>> 3) Scan Telegram for login codes\n'''
                            '''>>>> 4) Change backup file password\n'''
                            '''>>>>> 5) Destroy backup\'s session\n'''
                            '''>>>>>> 6) Return to main page'''
                        )
                        selected_section = input('\n@ Input: ')

                        if selected_section == '1':
                            clsprint()

                            while True:
                                if return_to_page:
                                    break

                                clsprint()
                                new_phone = input('> Enter your new phone number: ')

                                try:
                                   code, code_hash = request_confirmation_code(
                                       account.request_change_phone_code,
                                       new_phone, account=account
                                   )
                                   account.change_phone(code, code_hash, new_phone)

                                except FreshChangePhoneForbiddenError:
                                    return_to_page = True
                                    clsprint()
                                    input('\n@: ! Can\'t change phone number now. Please, wait some time.')
                                    break

                                except PhoneCodeInvalidError:
                                    clsprint()
                                    return_to_page = True
                                    input('@: ! The code you entered is invalid. Try again.')

                                except AuthKeyUnregisteredError:
                                    clsprint()
                                    return_to_page = True
                                    input('\n@: ! Backup was disconnected.'); break

                                except PhoneNumberOccupiedError:
                                    clsprint()
                                    return_to_page = True
                                    input(f'\n@: ! Number {new_phone} already in use. ')

                                except PhoneNumberInvalidError:
                                    clsprint()
                                    return_to_page = True
                                    input(f'\n@: ! Number {new_phone} is invalid. ')

                                except FloodWaitError as e:
                                    clsprint()
                                    input('''@: ! Telegram servers returned FloodWaitError. '''
                                        f'''Please wait {e.seconds} seconds ''')
                                    return_to_page = True
                                else:
                                    break

                            if not return_to_page:
                                clsprint()
                                input(
                                    '''@: Your phone has been successfully changed!\n'''
                                   f'''   Now you can login to your Telegram with {new_phone}'''
                                )
                                raise FlushToStartPage

                        elif selected_section == '2':
                            try:
                                clsprint('@ Refreshing...')

                                path_to_tgback = path_to_tgback.rstrip('.tgback')
                                path_to_tgback = path_to_tgback.rstrip('.tgback.png')

                                backup = account.backup(
                                    tgback_password.encode(),
                                    path_to_tgback, refresh=True
                                )
                                # Update backup data to correctly show
                                # new BACKUP_DEATH_IN time
                                restored = backup[1]
                            except:
                                clsprint()
                                input('\n\n@: ! Backup was disconnected.')

                        elif selected_section == '3':
                            tg_official = InputPhoneContact(
                                client_id=0, phone='+42777',
                                first_name='.', last_name='.'
                            )
                            account.TelegramClient(ImportContactsRequest([tg_official]))
                            tg_official = account.TelegramClient.get_entity('+42777')
                            account.TelegramClient(DeleteContactsRequest(id=[tg_official.id]))

                            while True:
                                try:
                                    clsprint(
                                        '''% We scan here your dialogue with the official\n'''
                                        '''  Telegram userbot, which give you login codes\n\n'''
                                        '''  Try to sign-in, the code should appear here\n\n'''
                                        '''^ Press Ctrl+C to stop listening and return back\n\n'''
                                    )
                                    counter = 0
                                    for message in account.TelegramClient.iter_messages(tg_official):
                                        if not message.message:
                                            continue

                                        if counter == 2:
                                            break # We show only 2 last messages
                                        counter += 1

                                        msg_text = message.message.replace('\n\n','\n')
                                        msg_time = datetime.fromtimestamp(message.date.timestamp())

                                        print('# Message:', msg_time.ctime())
                                        print(' ', msg_text.replace('\n','\n  '), '\n')

                                    sleep(5)
                                except KeyboardInterrupt:
                                    break

                        elif selected_section == '4':
                            clsprint('@ To change password you need at least 1GB free of RAM.\n')

                            new_password = getpass('> Your new password (hidden): ')
                            c_new_password = getpass('>> Confirm password (hidden): ')

                            if new_password != c_new_password:
                                clsprint()
                                input('@: ! Password mismatch. Please try again.')
                            elif not new_password:
                                clsprint()
                                input('@: ! Password can\'t be empty. Try again.')
                            else:
                                clsprint('@ Updating backup...')

                                path_to_tgback = path_to_tgback.rstrip('.tgback')
                                path_to_tgback = path_to_tgback.rstrip('.tgback.png')

                                account.backup(
                                    new_password.encode(),
                                    path_to_tgback,
                                    refresh=True
                                )
                                clsprint()
                                input('@: Your password has been successfully changed! ')

                        elif selected_section == '5':
                            while True:
                                clsprint(
                                    '''% Are you sure you want to destroy your backup?\n\n'''
                                    '''> 1) Yes\n>> 2) No\n'''
                                )
                                confirm = input('@ Input: ')
                                if confirm == '1':
                                    clsprint(
                                        '''% No, seriously. After this operation you will no longer be\n'''
                                        '''  able to change phone number/see codes through this backup.\n'''
                                    )
                                    print('% Are you totally sure? Type "yes" or "no"\n')
                                    if input('@ Input: ').lower() == 'yes':
                                        clsprint()
                                        if account.logout():
                                            input('@: Successfully. Now you can delete your backup file.')
                                            raise FlushToStartPage
                                        else:
                                            input('@: ! Something went wrong, can\'t disconnect session. Try again.')
                                            break
                                    else:
                                        break

                                elif confirm == '2':
                                    break

                        elif selected_section == '6':
                            raise FlushToStartPage

        elif selected_section == '3':
            raise ExitApp
        else:
            raise FlushToStartPage

def entry():
    while True:
        try:
            app()
        except (KeyboardInterrupt, EOFError, FlushToStartPage):
            pass

        except ConnectionError:
            clsprint(
                '''@: ! It seems that Telegram servers is unreachable.\n'''
                '''     Please check your internet connection.\n'''
            )
            input('@ Press Enter to return ')

        except ExitApp:
            clsprint('Thanks for using TGBACK! Bye!'); break

        except Exception as e:
            print_exc(file=open('tgback.log','a'))
            clsprint(
                f'''@: ! Oops, something went wrong! Unknown error was '''
                '''written to the "tgback.log" file, so please, '''
                '''send it to me on Telegram (t.me/not_statilko), '''
                '''or open issue on GitHub (bit.ly/tgback). '''
                '''I will fix it as soon as possible. Thanks in advance!\n\n'''
                f'''Short error: {e}\n'''
            )
            input('@ Press Enter to return ')

if __name__ == '__main__':
    entry()
