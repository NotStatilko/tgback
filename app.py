#!/usr/bin/python3

print('\n' * 100 + '@ TGBACK is loading...')

import os.path

from tools import (
    QR_ERROR, scanqrcode,
    restore, VERSION, QR_AVAILABLE, 
    TelegramAccount, make_scrypt_key
)
from sys import platform
from getpass import getpass
from traceback import print_exc
from os import system as os_system

from datetime import datetime
from time import ctime, strftime, sleep

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

            '''> 0) Quick help & What it is?\n'''
            '''>> 1) Backup Telegram account\n'''
            '''>>> 2) Open TGBACK backup file\n'''
            '''>>>> 3) Exit from TelegramBackup'''

            '''\n\n% Press Ctrl+C to back here'''
        )
        selected_section = input('\n@ Input: ')

        if selected_section and selected_section in '0123':
            break

    return_to_main = False

    while True:
        if return_to_main:
            raise FlushToStartPage 

        if selected_section == '0':
            clsprint(
                '''  The TGBACK (a.k.a) TelegramBackup is a simple CMD app\n'''
                '''  that was created in response to the strange Telegram\n'''
                '''  behaviour: to sign-in your account you *should* have\n'''
                '''  an access to a phone number (SIM card) it linked. If you\n'''
                '''  will lost your SIM, then you lost your Telegram account.\n\n'''

                '''  This (seems to me a) problem can be fixed in a three ways:\n'''
                '''      1. You can make an extra log-in on your other device\n'''
                '''      2. You can backup TelegramDesktop's TDATA folder (Google it)\n'''
                '''      3. You can use TGBACK, and it will save & encrypt session\n\n'''

                '''  If any session (device logged-in) is linked to your account, then\n'''
                '''  you will receive a login code from official Telegram userbot, so\n'''
                '''  this can help to omit this "problem", if it\'s enough for you -- good!\n'''
                '''  Don't use TGBACK! But if you don\'t have second device, we can help you!\n\n'''

                '''  In short, this app will sign-in to your account as new session (see\n'''
                '''  Settings -> Devices in Telegram if you don\'t understand what it is)\n'''
                '''  and will, again, save and encrypt necesarry data of itself [session] to file,\n'''
                '''  so you can use it later to change phone number linked to your account or\n'''
                '''  retrieve last messages from the Telegram userbot, so you can receive a code.\n\n'''

                '''  After backup creation you will receive a *.tgback file and an image with QR code,\n'''
                '''  both encapsulates an identical data in encrypted form, so you can save any.\n\n'''

                '''  You will need to *refresh it* every three months, so Telegram will not disconnect it\n'''
                '''  due the inactivity. One of Telegram update showed that this limit, probably, can\n'''
                '''  be extended up to five-six months, but i don\'t want to risk of a peoples data, so 3.\n\n'''

                '''!!! WARNING !!!\n\n'''

                '''  We will save a data that is enough to gain A FULL ACCESS TO YOUR TELEGRAM ACCOUNT!!\n\n'''
                '''  While the developer DOESN'T transfer any of your private data (sources: bit.ly/tgback)\n'''
                '''  the other "bad guys" can make an app from codebase that will make an awful things.\n\n'''
                '''  Please note that connected TGBACK session SHOULDN'T be active/online from time you\n'''
                '''  refreshed it. If you found some suspicious activity then IMMEDIATELY disconnect it!\n'''
                '''  This can be easily done via TGBACK/Telegram(Settings->Devices->Select TGBACK->Disconnect)\n\n'''

                '''  Please, get the .EXE file or build ONLY from the official sources: \n'''
                '''      1. https://github.com/NotStatilko/tgback\n'''
                '''      2. https://t.me/nontgback (dev. channel)\n\n'''

                '''  Use STRONG passwords. This app programmed in a way that for any password generation\n'''
                '''  attempt you will need to give a 1GB of RAM for about a second-two, so it's VERY hard to\n'''
                '''  bruteforce, but still not impossible. An author ISN'T a professional crypto-man, so be\n'''
                '''  careful. If you\'re aware what is AES / Scrypt and have a time, - then, please, check sources\n'''
                '''  and write me (t.me/not_statilko, or email: thenonproton@pm.me) if you found any vulnerability.\n\n'''
                
                '''  There wasn't any security-related reports up to this day. Just use TGBACK correctly.\n\n'''

                '''** Regards. Don't trust, verify. 2019-2022, Non.'''
            )
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
                                    input('@: ! Password mismatch! Try again.\n')
                                elif not tgback_password:
                                    input('@: ! Password can\'t be empty.\n')
                                else:
                                    break

                            clsprint('@ Creating key & making backup...')

                            filename = account.backup(
                                tgback_password.encode(), 
                                tgback_filename
                            )
                            clsprint()
                            input(f'@ Successfully encrypted and backuped! ({filename})')
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

                    if not os.path.exists(config):
                        clsprint()
                        input('@: ! Can\'t open config file. Check your path. ')

                    elif os.path.isdir(config):
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
                                filename = account.backup(config[2].encode(), config[3])

                                clsprint()
                                input(f'@ Successfully encrypted and backuped! ({filename})')

                                return_to_main = True; break

                        except ConnectionError:
                            raise ConnectionError
                        except OSError:
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

            if not os.path.exists(path_to_tgback):
                clsprint()
                input(f'@: ! Can\'t find .tgback {backup_type}. Check entered path.')
                raise FlushToStartPage

            elif os.path.isdir(path_to_tgback):
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

                                account.backup(
                                    tgback_password.encode(), 
                                    path_to_tgback,
                                    refresh=True
                                )
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
                                clsprint('@ Ok. Updating backup...')

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
