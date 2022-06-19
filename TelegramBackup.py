print('\n' * 100 + '@ TGBACK is loading...')

import os.path

from tgback_utils import (
    restore, VERSION, qr_available, 
    TelegramAccount, TgbackAES,
    image_error, scanqrcode
)
from getpass import getpass
from sys import platform
from traceback import print_exc
from time import ctime, strftime, sleep

from reedsolo import ReedSolomonError

from asyncio import run as asyncio_run
from os import system as os_system

from telethon.errors.rpcerrorlist import (
    AuthKeyUnregisteredError, PhoneCodeInvalidError,
    PasswordHashInvalidError, PhoneNumberOccupiedError,
    PhoneNumberInvalidError, FloodWaitError, PhoneCodeEmptyError,
    PhoneCodeInvalidError, FreshChangePhoneForbiddenError
)
from telethon.tl.functions.contacts import (
    ImportContactsRequest, DeleteContactsRequest
)
from telethon.tl.types import InputPhoneContact

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
                f''' - TGBACK {VERSION} (bit.ly/tgback) -\n\n'''
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
                await main()

            clear_terminal()
            if selected_section == '0':
                clear_terminal()
                print(
                    '''  The TGBACK (a.k.a) TelegramBackup is a simple CMD app\n'''
                    '''  that was created in response to the strange Telegram\n'''
                    '''  behaviour: to sign-in your account you *should* have\n'''
                    '''  an access to a phone number (SIM card) it linked. If you\n'''
                    '''  will lost your SIM, then you lost your Telegram account.\n\n'''

                    '''  This (seems to me a) problem can be fixed in two ways:\n'''
                    '''      1. You can make an extra log-in on your other device\n'''
                    '''      2. You can use TGBACK, and it will save & encrypt session\n\n'''

                    '''  If any session (device logged-in) is linked to your account, then\n'''
                    '''  you will receive a login code from official Telegram userbot, so\n'''
                    '''  this can help to omit this "problem", if it\'s enough for you -- good!\n'''
                    '''  Don't use TGBACK! But if you don\'t have second device, we can help you!\n\n'''

                    '''  In short, this app will sign-in to your account as new session (see\n'''
                    '''  Settings -> Devices in Telegram if you don\'t understand what it is)\n'''
                    '''  and will, again, save and encrypt necesarry data of itself [session] to file,\n'''
                    '''  so you can use it later to change phone number linked to your account or\n'''
                    '''  retrieve last messages from the Telegram userbot, so you can receive a code.\n\n'''

                    '''  After backup creation you will receive a *.tgback file and a image with QR code,\n'''
                    '''  both encapsulates an identical data in encrypted form, so you can save any.\n\n'''

                    '''  You will need to *refresh it* every two months, so Telegram will not disconnect it\n'''
                    '''  due the inactivity. Recent Telegram update showed that this limit, probably, can\n'''
                    '''  be extended up to five-six months, but i don\'t want to risk of a peoples data, so 2.\n\n'''

                    '''!!! WARNING !!!\n\n'''

                    '''We will save a data that is enough to gain A FULL ACCESS TO YOUR TELEGRAM ACCOUNT!\n'''
                    '''While the developer DOESN\'t transfer any of your private data (sources: bit.ly/tgback)\n'''
                    '''any of other "bad peoples" can make an app from codebase that will make a bad things.\n'''
                    '''Please note that connected TGBACK session SHOULDN'T be active/online from time you\n'''
                    '''refreshed it. If you found some suspicious activity then IMMEDIATELY disconnect it!\n'''
                    '''This can be easily done via TGBACK/Telegram(Settings->Devices->Select TGBACK->Disconnect)\n\n'''

                    '''Please, get the .EXE file or build ONLY from the official sources: \n'''
                    '''    1. https://github.com/NotStatilko/tgback\n'''
                    '''    2. https://t.me/nontgback (dev. channel)\n\n'''

                    '''Use ONLY strong passwords. This app programmed in a way that for any password generation\n'''
                    '''attempt you will need to give a 1GB of RAM for about a second-two, so it VERY hard to\n'''
                    '''bruteforce, but still not impossible. An author ISN\'T a professional crypto-man, so be\n'''
                    '''careful. If you\'re aware what is AES / Scrypt and have a time, - then, please, check sources\n'''
                    '''and write me (t.me/not_statilko, or email: thenonproton@pm.me) if you found any vulnerability.\n\n'''
                    
                    '''There was not any security-related reports up to this day. Just use TGBACK correctly.\n\n'''

                    '''Regards. Don\'t trust anyone. 2019-2022, Non.'''
                )
                input('\n\n@ Press Enter to exit ')

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
                            password = getpass('>> Your Telegram password (hidden): ')
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
                                    print('@ To create backup you need at least 1GB free of RAM.\n')
                                    tgback_password = getpass('> Backup password (hidden): ')
                                    c_tgback_password = getpass('>> Re-enter password (hidden): ')

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
                        print('@ To decrypt backup you need at least 1GB free of RAM.\n')
                        tgback_password = getpass(f'>> Password to .tgback {backup_type} (hidden): ')
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
                                '''> 1) Change phone number of account\n'''
                                '''>> 2) Refresh .tgback backup session\n'''
                                '''>>> 3) Scan Telegram for login codes\n'''
                                '''>>>> 4) Change backup file password\n'''
                                '''>>>>> 5) Destroy backup\'s session\n'''
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
                                client = account._TelegramClient

                                tg_official = InputPhoneContact(
                                    client_id=0, phone='+42777', 
                                    first_name='.', last_name='.'
                                )
                                await client(ImportContactsRequest([tg_official]))
                                tg_official = await client.get_entity('+42777')
                                await client(DeleteContactsRequest(id=[tg_official.id]))

                                while True:
                                    try:
                                        clear_terminal()
                                        print(
                                            '''% We scan here your dialogue with the official\n'''
                                            '''  Telegram userbot, which give you login codes\n\n'''
                                            '''  Try to sign-in, the code should appear here\n\n'''
                                            '''^ Press Ctrl+C to stop listening and return back\n\n'''
                                        )
                                        counter = 0
                                        async for message in client.iter_messages(tg_official):
                                            if not message.message:
                                                continue

                                            if counter == 2: 
                                                break # We show only 2 last messages
                                            counter += 1
                                            
                                            msg_text = message.message.replace('\n\n','\n')

                                            print('# Message:', str(message.date))
                                            print(' ', msg_text.replace('\n','\n  '), '\n')

                                        sleep(5)
                                    except KeyboardInterrupt:
                                        break

                            elif selected_section == '4':
                                clear_terminal()
                                print('@ To change password you need at least 1GB free of RAM.\n')
                                new_password = getpass('> Your new password (hidden): ')
                                c_new_password = getpass('>> Confirm password (hidden): ')
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
