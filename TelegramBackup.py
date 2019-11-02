print('\n' * 100 + '@ TelegramBackup is loading...')

import os.path

from base64 import b64encode
from NonCipher import NonCipher
from os import system as os_system_
from asyncio import run as asyncio_run
from telethon.errors import FloodWaitError

from tgback_utils import (
    TelegramAccount, restore, make_session
)

def clear_terminal():
    os_system_('cls || clear')
    print('\n' * 50)


async def main():
    try:
        clear_terminal()
        while True:
            print(''' - TelegramBackup 2.0 -\n\n'''
                  '''> 1) Backup Telegram account\n'''
                  '''>> 2) Change phone number\n'''
                  '''>>> 3) Decrypt .tgback backup\n'''
                  '''>>>> 4) Exit from TelegramBackup'''
                  '''\n\n% Press Ctrl+C in any mode for returning to this page'''
            )
            selected_section = input('\n@ Input: ')
            if selected_section in list('1234') + ['what\'s new?']:
                break
            clear_terminal()

        while True:
            clear_terminal()
            if selected_section == '1':
                api_id = input('> API ID: ')
                clear_terminal()
                api_hash = input('>> API Hash: ')
                clear_terminal()
                phone = input('>>> Phone number: ')
                try:
                    clear_terminal()
                    print('@ Checking for correctness...')
                    account = TelegramAccount(
                        api_id, api_hash, phone
                    )
                    await account.connect()
                    clear_terminal()
                    print('@ Requesting confirmation code...')
                    await account.request_code()
                    clear_terminal()

                    code = input('> Confirmation Code: ')
                    password = input('>> Your Telegram password: ')
                    clear_terminal()

                    print('@ Trying to login...')
                    try:
                        await account.login(password,code)
                        clear_terminal()

                        tgback_filename = input('> Backup filename: ')
                        tgback_password = input('>> Backup password: ')

                        clear_terminal()
                        print('@ Backup password generating, please wait...')

                        file = account.backup(tgback_password, tgback_filename)
                        clear_terminal()

                        account.remove_session()
                        input('@ Successfully backuped and encrypted! ({0})'.format(file))
                        await main()

                    except (KeyboardInterrupt, EOFError):
                        await main()
                    except:
                        input('\n@: ! Invalid password or code. Try again.')

                except FloodWaitError as e:
                    clear_terminal()
                    input('''@: ! Telegram servers return FloodWaitError. '''
                        '''Please wait {0} seconds '''.format(e.seconds))
                    await main()
                except:
                    clear_terminal()
                    input('''@: ! App Invalid! Copy and paste from the '''
                          '''site my.telegram.org. Help: bit.ly/tgback '''
                    )
                finally:
                    account.remove_session()

            elif selected_section == '2':
                clear_terminal()
                path_to_tgback = input('> Path to .tgback file: ')
                if not os.path.exists(path_to_tgback):
                    input('@: ! Can\'t open .tgback file. Check your path. ')
                    await main()
                else:
                    tgback_password = input('>> Password to .tgback file: ')
                    clear_terminal()
                    print('@ Backup password generating, please wait...')
                    try:
                        restored = restore(path_to_tgback, tgback_password)
                        restored_backup = restored[0]
                        primary_hash, hash_of_input_data = restored[1]
                    except:
                        clear_terminal()
                        input('\n@: ! Incorrect Password. ')
                        await main()
                    else:
                        clear_terminal()
                        make_session(restored_backup)
                        account = TelegramAccount(*restored_backup[1], restored_backup[0])
                        await account.connect()
                        while True:
                            clear_terminal()
                            new_phone = input('> Enter your new phone number: ')
                            try:
                               code_hash = await account.request_change_phone_code(new_phone)
                            except:
                                input('\n@: ! Number is invalid or already in use. ')
                            else: break

                        while True:
                            clear_terminal()
                            print('>> Confirmation code has been sent to ' + new_phone)
                            code = input('@ >> Code: ')

                            try:
                                await account.change_phone(code, code_hash, new_phone)
                            except:
                                input('\n@: ! Invalid code. Try again or hit Ctrl+C. ')
                            else: break

                        clear_terminal()
                        account.remove_session()

                        new_backup = (new_phone, restored_backup[1], restored_backup[2])
                        nc = NonCipher(primary_hash=primary_hash, hash_of_input_data=hash_of_input_data)
                        nc.init()

                        with open(path_to_tgback,'wb') as f:
                            f.write(b64encode(nc.encrypt(repr(new_backup)).encode()))

                        input('''@: Your phone has been successfully changed! '''
                            '''Now you can login to your Telegram account with phone ''' + new_phone + ' ! ')
                        await main()

            elif selected_section == '3':
                path_to_backup = input('> Direct path to .tgback file: ')
                if os.path.exists(path_to_backup):
                    tgback_password = input('>> Password for .tgback file: ')

                    clear_terminal()
                    print('@ Backup password generating, please wait...')

                    name = os.path.split(path_to_backup)[1].split('.tgback')[0]

                    try:
                        restored = restore(path_to_backup, tgback_password)
                        clear_terminal()
                    except:
                        input('\n@: ! Incorrect Password. ')
                        await main()
                    else:
                        with open(name + '.dtgback','wb') as f:
                            f.write(repr(restored).encode())

                        input('@ Successfully decrypted! ({0})'.format(name + '.dtgback'))
                        await main()
                else:
                    input('\n@: ! Can\'t open .tgback file. Please check your path.')

            elif selected_section == '4':
                exit()

            elif selected_section == 'what\'s new?':
                input('@: # New mode and first stable version! bit.ly/tgback. NonSense. ')
                await main()

    except (KeyboardInterrupt, EOFError):
        await main()


asyncio_run(main())
