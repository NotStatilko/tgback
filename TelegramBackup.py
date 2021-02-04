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
from os import system as os_system

from telethon.errors.rpcerrorlist import (
    AuthKeyUnregisteredError, PhoneCodeInvalidError,
    PasswordHashInvalidError, PhoneNumberOccupiedError,
    PhoneNumberInvalidError, FloodWaitError, PhoneCodeEmptyError,
    PhoneCodeInvalidError, FreshChangePhoneForbiddenError
)
if platform.startswith('win'):
    clear_command = 'cls'
elif platform.startswith('cygwin'):
    clear_command = 'printf "\033c"'
else:
    clear_command = "printf '\33c\e[3J' || cls || clear"

def clear_terminal():
    os_system(clear_command)
    print('\n' * 100)

async def main():
    try:
        async def request_confirmation_code(request_coroutine, phone: str, account: TelegramAccount=None) -> tuple:
            request_code, code_hash = True, None
            phone = phone.replace(' ','')
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
                '''> 0) Switch to the help page\n'''
                '''>> 1) Backup Telegram account\n'''
                '''>>> 2) Open .tgback backup\n'''
                '''>>>> 3) Exit from TelegramBackup'''
                '''\n\n% Press Ctrl+C to back here'''
            )
            selected_section = input('\n@ Input: ')
            if selected_section and selected_section in '0123':
                break

        return_to_main = False
        while True:
            if return_to_main:
                await main()

            clear_terminal()
            if selected_section == '0':
                while True:
                    clear_terminal()
                    print(
                        '''@ Welcome You!\n\n'''
                        '''   01) Why is it needed?\n'''
                        '''   02) How it works?\n'''
                        '''   03) Can tgback back up my messages?\n'''
                        '''   04) What information do you store?\n'''
                        '''   05) Do you transfer any of my data?\n'''
                        '''   06) Why we are need to refresh backups?\n'''
                        '''   07) Can i use tgback on my Android?\n'''
                        '''   08) What encryption is used in tgback?\n'''
                        '''   09) What version do you prefer me to use?\n'''
                        '''   10) Passwords isn\'t visible. Why?\n'''
                        '''   11) QR features is unavailable. Why?\n'''
                        '''   12) Can i use tgback with TOR network?\n'''
                        '''   13) Tell me more about backup\'s refreshing and disconnecting.\n'''
                        '''   14) I found a bug or have an idea. How can i help?\n'''
                        '''   15) I don\'t trust you. Any alternatives?\n\n'''
                        '''00) Back to the main page\n'''
                    )
                    mode = input('@ Input: ')
                    mode = mode if not mode else mode.zfill(2)
                    clear_terminal()

                    if mode == '00': 
                        break

                    elif mode == '01':
                        print(
                            '''01) Why is it needed?\n\n'''
                            '''o Telegram is designed so that you cannot enter your account '''
                            '''without receiving a code. This code can be obtained in two ways: '''
                            '''by receiving the code in Telegram or on your phone. The first method '''
                            '''is available only if you are logged into your account from another device '''
                            '''(for example, the desktop version). If you are logged into your account on only '''
                            '''one device (or not logged at all), then if you lose access to your SIM card, you '''
                            '''will also lose access to your Telegram account forever.'''
                        )
                    elif mode == '02':
                        print(
                            '''02) How it works?\n\n'''
                            '''o Telegram has an open client API on which official clients are built. Anyone who knows '''
                            '''one of the many programming languages can create their own client. Tgback can be called a '''
                            '''very stripped-down client. This program can only log into the account and change the number. '''
                            '''When you log in to your account, Telegram sends you a special session token, which is used to manage '''
                            '''your account. This rule works on all clients, including official ones. Tgback saves this token '''
                            '''along with metadata (for example, your account's username or the time when the backup will be off) '''
                            '''and encrypts it to a file and QR. Whenever you need, you can decrypt this backup and change the phone '''
                            '''number (if you have lost access to the old one) or enter the TelegramDesktop. In fact, Tgback adds an '''
                            '''alternative login method. Your session token is not transferred anywhere and all code is open. However, '''
                            '''beware, the only safe sources you can get Tgback from are these:\n\n   '''
                            '''o https://github.com/NotStatilko/tgback (bit.ly/tgback)\n   o https://t.me/nontgback'''
                        )
                    elif mode == '03':
                        print(
                            '''03) Can tgback back up my messages?\n\n'''
                            '''o No, tgback allows you only create backups from which you can login or change your phone number. '''
                            '''However, session token (which tgback backups store) can allow get FULL access over your account. '''
                            '''So don\'t use very simple passwords, such as "qwerty" or "password1234".'''
                        )
                    elif mode == '04':
                        print(
                            '''04) What information do you store?\n\n'''
                            '''o Any at all. Tgback backups itself store token session, account username, account id, '''
                            '''time when backup will be disconnected and other data needed by tgback. Nothing will be transferred. '''
                            '''To get more details you can visit official GitHub page on bit.ly/tgback.'''
                        )
                    elif mode == '05':
                        print('05) Do you transfer any of my data?\n\no No.')
                    
                    elif mode == '06':
                        print(
                            '''06) Why we are need to refresh backups?\n\n'''
                            '''o Because Telegram (seems to) disconnect inactive sessions. At the time of discovery this problem, '''
                            '''the disabled backup had not been refreshed for six months, but this has not been sufficiently researched. '''
                            '''At the moment, the backup needs to be refreshed every two months, and you recieve a delayed message '''
                            '''one week in advance as a reminder. Please note that Tgback doesn't turn off backups by itself after two '''
                            '''months, and you will probably still have about two more months. Disconnection of sessions is performed by the Telegram server.'''
                        )
                    elif mode == '07':
                        print(
                            '''07) Can i use tgback on my Android?\n\n'''
                            '''o Sure, you can use Termux which doesn\'t require root. Check out installation steps for Linux on official '''
                            '''tgback\'s Github page: bit.ly/tgback'''
                        )
                    elif mode == '08':
                        print(
                            '''08) What encryption is used in tgback?\n\n'''
                            '''o Started from 4.0 version of tgback, the AES-256 CBC with Scrypt (1 GB of RAM) as PBKDF.'''
                        )
                    elif mode == '09':
                        print(
                            '''09) What version do you prefer me to use?\n\n'''
                            '''o Latest which >= v4.0. Others is considered as not secure.'''
                        )
                    elif mode == '10':
                        print(
                            '''10) Passwords isn't visible. Why?\n\n'''
                            '''o The password is not displayed by default but you enter it. If you have any problems '''
                            '''with creating a backup, you can use the config-file (mode 1->2). Create an empty file and fill it with this template:\n\n'''
                            '''   o "phone_number; telegram_password; backup_password; backup_filename"'''
                        )
                    elif mode == '11':
                        print(
                            '''11) QR features is unavailable. Why?\n\n'''
                            '''If you on linux then make sure that you already *installed the LibZBar package. If you are on other system, '''
                            '''then open issue on official tgback *repository.\n\n   o sudo apt install libzbar0\n   o https://github.com/NotStatilko/tgback'''
                        )
                    elif mode == '12':
                        print('12) Can i use tgback with TOR network?\n\no Sure, use torsocks or torify for this.')
                    
                    elif mode == '13':
                        print(
                            '''13) Tell me more about backup's refreshing and disconnecting\n\n'''
                            '''o After backup refreshing you get new backups, but you can also use the old ones to log '''
                            '''into your account or change the number, they will just show the wrong time before the date when '''
                            '''the backup needs to be refreshed. To destroy a backup, it\'s not enough to delete only the file, you need '''
                            '''to disconnect your backup session. This can be done in two ways: either through the tgback itself or via Telegram. '''
                            '''After disconnecting the session in any way, all copies of backups associated with this session cease '''
                            '''to be active. Also, please note that changing the password with which you encrypted the backup only changes '''
                            '''the password for the backup that you opened. If the attacker somehow received the password for your backup, '''
                            '''immediately log in to Telegram and disconnect all sessions that you do not recognize as your own. '''
                        )
                    elif mode == '14':
                        print(
                            '''14) I found a bug or have an idea. How can i help?\n\n'''
                            '''o You are always welcome on tgback\'s GitHub! Open issues or send pull-requests!\n\n   '''
                            '''o https://github.com/NotStatilko/tgback (bit.ly/tgback)'''
                        )
                    elif mode == '15':
                        print(
                            '''5) I don't trust you. Any alternatives?\n\n'''
                            '''o You can back up the Telegram\'s tdata folder or log in to more than one device. '''
                            '''You can also give a reaction to *this commit and maybe Telegram will add TOTP codes.\n\n   '''
                            '''o https://github.com/telegramdesktop/tdesktop/issues/10253'''
                        )
                    else: continue
                    input('\n@ Press Enter to back ')

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
                                clear_terminal()
                                while True:
                                    print('@ To create backup you need at least 1GB free for now.\n')
                                    tgback_password = getpass('> Backup password: ')
                                    c_tgback_password = getpass('>> Re-enter password: ')

                                    clear_terminal()
                                    if tgback_password != c_tgback_password:
                                        print('@: ! Password mismatch! Try again.\n')
                                    elif not tgback_password:
                                        print('@: ! Password can\'t be empty.\n')
                                    else:
                                        break

                                clear_terminal()
                                print('@ Creating key with your password...')

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

                        except (PhoneNumberInvalidError, TypeError):
                            clear_terminal()
                            input(f'@: ! The provided number ({phone}) is invalid. Try again.')
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
                                    print('@ Creating key with your password...')
                                    filename = await account.backup(config[2],config[3])
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
                    while True:
                        clear_terminal()
                        print('@ To decrypt backup you need at least 1GB free for now.\n')
                        tgback_password = getpass(f'>> Password to .tgback {backup_type}: ')
                        if not tgback_password:
                            clear_terminal()
                            input('@: ! Password can\'t be empty. Try again or press Ctrl+C.')
                        else: break
                    clear_terminal()
                    print('@ Creating key with your password...')
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
                                                print('@ Scanning Telegram auth QR code...')
                                                token = scanqrcode(qrcode_path).split(b'token=')[1]
                                                await account.accept_login_token(token)
                                                clear_terminal()
                                                input('@: Successfully logged in! ')
                                                break
                                            except:
                                                clear_terminal()
                                                input('''@: ! Can\'t log in. Try to increase '''
                                                      '''size of QR or wait 30 seconds and screenshot new QR code.''')
                                        else:
                                            input(
                                                '''@: ! Sorry, i can\'t open path that you provided. '''
                                                '''Re-screenshot new QR and check your path.'''
                                            )
                                    elif choice == '2':
                                        break

                            elif selected_section == '4':
                                clear_terminal()
                                print('@ To change password you need at least 1GB free for now.\n')
                                new_password = getpass('> Your new password: ')
                                c_new_password = getpass('>> Confirm password: ')
                                if new_password != c_new_password:
                                    clear_terminal()
                                    input('@: ! Password mismatch. Please try again.')
                                elif not new_password:
                                    clear_terminal()
                                    input('@: ! Password can\'t be empty. Try again.')
                                else:
                                    clear_terminal()
                                    print('@ Creating key with your password...')
                                    restored[0] = TgbackAES(b'0')._make_scrypt_key(new_password.encode()).digest()
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
