print('\n' * 100 + '@ TelegramBackup is loading...')

import os.path

from asyncio import run as asyncio_run
from os import system as os_system_

from tgback import (
    TelegramAccount, check_app, restore
)


def clear_terminal():
    os_system_('cls || clear')
    print('\n' * 100)


async def main():
    try:
        clear_terminal()
        while True:
            print(''' - TelegramBackup 1.1 -\n\n'''
                  '''> 1) Backup Telegram account\n'''
                  '''>> 2) Change phone number\n'''
                  '''>>> 3) Decrypt .tgback backup\n'''
                  '''>>>> 4) Exit from TelegramBackup'''
                  '''\n\n% Press Ctrl+C in any mode for returning to this page'''
            )
            selected_section = input('\n@ Input: ')
            if selected_section in list('1234'):
                break
            clear_terminal()

        while True:
            clear_terminal()
            if selected_section == '1':
                api_id = input('> API ID: ')
                clear_terminal()
                api_hash = input('>> API Hash: ')
                clear_terminal()
                phone = input('>>> Phone Number: ')

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
                        input('@ Successfully backuped and encrypted! ({0})'.format(file))
                        await main()
                    except (KeyboardInterrupt, EOFError):
                        await main()
                    except:
                        input('\n@: ! Invalid password or code. Try again.')

                except:
                    input('''\n\n@: ! App Invalid! Copy and paste from the '''
                          '''site my.telegram.org. Help: bit.ly/tgback'''
                    )
            elif selected_section == '2':
                input('@ Work in Progress. Check out bit.ly/tgback for updates.')
                await main()

            elif selected_section == '3':
                path_to_backup = input('> Direct path to .tgback file: ')
                if os.path.exists(path_to_backup):
                    tgback_password = input('>> Password for .tgback file: ')

                    clear_terminal()
                    print('@ Backup password generating, please wait...')

                    name = os.path.split(path_to_backup)[1].split('.tgback')[0]

                    restored = restore(path_to_backup, tgback_password)
                    if len(restored) == 1 or not check_app(restored[0], restored[1]):
                        input('\n@: ! Incorrect Password. Please, try again.')
                    else:
                        with open(name + '.dtgback','w') as f:
                            f.write(' '.join(restored))
                        input('@ Successfully decrypted! ({0})'.format(name + '.dtgback'))
                        await main()
                else:
                    input('\n@: ! Can\'t open .tgback file. Please check your path.')

            elif selected_section == '4':
                exit()
                                        
    except (KeyboardInterrupt, EOFError):
        await main()


asyncio_run(main())
