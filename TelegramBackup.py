print('\n' * 35 + '@ TelegramBackup is loading...')

import os.path

from time import ctime
from getpass import getpass
from traceback import print_exc
from os import system as os_system_
from asyncio import run as asyncio_run
from telethon.errors import FloodWaitError
from telethon.errors.rpcbaseerrors import AuthKeyError

from tgback_utils import TelegramAccount, restore

def clear_terminal():
    os_system_('cls || clear'); print('\n' * 35)
    

async def main():
    try:
        clear_terminal()
        while True:                   
            print(
                ''' - TelegramBackup 3.0 -\n\n'''
                '''> 1) Backup Telegram account\n'''
                '''>> 2) Open .etgback backup\n'''
                '''>>> 3) Exit from TelegramBackup'''
                '''\n\n% Press Ctrl+C in any mode for returning to this page'''
            )
            selected_section = input('\n@ Input: ')
            if selected_section in '123':
                break                      

        while True:
            clear_terminal()
            if selected_section == '1':
                api_id = getpass('> API ID (hidden input): ')
                clear_terminal()
                api_hash = getpass('>> API Hash: ')
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
                    password = getpass('>> Your Telegram password: ')
                    clear_terminal()

                    print('@ Trying to login...')
                    try:
                        await account.login(password,code)
                        clear_terminal()

                        tgback_filename = input('> Backup filename: ')
                        tgback_password = getpass('>> Backup password: ')

                        clear_terminal()
                        print('@ Backup password generating, please wait...')

                        filename = await account.backup(tgback_password, tgback_filename)
                        clear_terminal()
                        
                        input(f'@ Successfully backuped and encrypted! ({filename})')
                        await main()

                    except (KeyboardInterrupt, EOFError):
                        await main()
                    except:
                        input('\n@: ! Incorrect password or code. Try again.')

                except FloodWaitError as e:
                    clear_terminal()
                    input('''@: ! Telegram servers return FloodWaitError. '''
                        f'''Please wait {e.seconds} seconds ''')
                    await main()
                except:
                    clear_terminal()
                    input('''@: ! App Invalid! Copy and paste from the '''
                          '''site my.telegram.org. Help: bit.ly/tgback '''
                    )                
            elif selected_section == '2':
                clear_terminal()
                path_to_tgback = input('> Path to .etgback file: ')
                if not os.path.exists(path_to_tgback):
                    input('@: ! Can\'t open .etgback file. Check your path. ')
                    await main()
                else:
                    tgback_password = getpass('>> Password to .etgback file: ')
                    clear_terminal()
                    print('@ Password for backup is generating, please wait...')
                    try:
                        restored = restore(path_to_tgback, tgback_password)
                        assert len(restored) == 8
                    except:                        
                        clear_terminal()                       
                        input('\n@: ! Incorrect Password. ')
                        await main()
                    else:
                        account = TelegramAccount(
                            *restored[:2], session=restored[3]
                        )
                        await account.connect()
                        while True:
                            clear_terminal()
                            return_to_page = False
                            print(
                                f'''% Hello, {restored[5] + restored[7]}! (id{restored[6]})\n\n'''
                                f'''@ Backup valid until {ctime(float(restored[4]))}\n'''
                                f'''@ API ID / API Hash: {restored[0][:4]}... / {restored[1][:4]}...\n\n'''                                                                                               
                                f'''> 1) Change account phone number\n'''
                                f'''>> 2) Refresh .etgback backup\n'''
                                f'''>>> 3) Return to main page'''
                            )                            
                            selected_section = input('\n@ Input: ')                                                                                                                                   
                            if selected_section == '1':                  
                                clear_terminal()                                                              
                                while True:
                                    clear_terminal()
                                    new_phone = input('> Enter your new phone number: ')
                                    try:
                                       code_hash = await account.request_change_phone_code(new_phone)
                                    except AuthKeyError:
                                        return_to_page = True
                                        input('\n@: ! Can\'t change phone number now. Please, wait some time.')
                                        break                                        
                                    except:                                       
                                        input('\n@: ! Number is invalid or already in use. ')
                                    else:
                                        break
                                
                                if not return_to_page:
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
                                    input('''@: Your phone has been successfully changed! '''
                                        f'''Now you can login to your Telegram account with phone {new_phone}!''')
                                    await main()
                            
                            elif selected_section == '2':
                                await account.refresh_backup(restored, path_to_tgback)
                                clear_terminal()
                                input('@ Successfully refreshed! | ')
                                
                            elif selected_section == '3':
                                await main()
                                
            elif selected_section == '3':
                raise SystemExit
            else:
                await main()
            
    except (KeyboardInterrupt, EOFError): await main()        
    except SystemExit: raise SystemExit    
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
        input('@ Press Enter to return |')
        await main()


asyncio_run(main())