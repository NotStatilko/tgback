print('\n' * 100 + '@ TelegramBackup is loading...')

import os.path

from asyncio import run as asyncio_run
from os import system as os_system_

from tgback import (
    TelegramAccount, check_app, restore
)

def os_system(arg):
    os_system_(arg)
    print('\n' * 100)

async def main():
    try:
        os_system('cls || clear')
        while True:
            print(''' - TelegramBackup 1.0 -\n\n'''
                  '''> 1) Backup Telegram\n'''
                  '''>> 2) Change phone number\n'''
                  '''>>> 3) Decrypt .tgback file\n'''
                  '''>>>> 4) Exit from Telegram Backup'''
            )
            selected_section = input('\n@ Input: ')
            if selected_section in list('1234'):
                break
            os_system('cls || clear')

        while True:
            os_system('cls || clear')
            if selected_section == '1':
                api_id = input('> API ID: ')
                api_hash = input('>> API HASH: ')
                phone = input('>>> Phone number: ')

                try:
                    os_system('cls || clear')
                    account = TelegramAccount(
                        api_id, api_hash, phone
                    )
                    await account.connect()
                    await account.request_code()

                    code = input('> Confirmation Code: ')
                    password = input('>> Your Telegram password: ')

                    try:
                        await account.login(password,code)
                        os_system('cls || clear')

                        tgback_filename = input('> Backup filename: ')
                        tgback_password = input('>> Backup password: ')

                        os_system('cls || clear')
                        print('@ Backup password generating, please wait...')

                        file = account.backup(tgback_password, tgback_filename)
                        input('@ Successfully backuped and encrypted! ({0})'.format(file))
                        await main()
                    except:
                        input('\n@: ! Invalid password or code. Try again.')

                except:
                    input('''\n\n@: ! App Invalid! Note that API ID '''
                          '''and API HASH just don't appear in the terminal. '''
                          '''Copy and paste from the site https://my.telegram.org'''
                    )
            elif selected_section == '2':
                input('@ Work in Progress. Check out bit.ly/tgback for updates.')
                await main()

            elif selected_section == '3':
                path_to_backup = input('> Direct path to .tgback file: ')
                if os.path.exists(path_to_backup):
                    tgback_password = input('>> Password for .tgback file: ')

                    os_system('cls || clear')
                    print('@ Backup password generating, please wait...')

                    name = os.path.split(path_to_backup)[1].split('.tgback')[0]

                    restored = restore(path_to_backup, tgback_password)
                    if len(restored) == 1 or not check_app(restored[0], restored[1]):
                        input('\n@: ! Incorrect Password. Please, try again.')
                    else:
                        with open(name + '.dtgback','w') as f:
                            f.write(' '.join(restored))
                        input('@ Successfully decrypted! ({0})'.format(name + 'dtgback'))
                        await main()
                else:
                    input('\n@: ! Can\'t find .tgback file. Please check your path')

            elif selected_section == '4':
                exit()

    except (KeyboardInterrupt, EOFError):
        await main()


asyncio_run(main())
