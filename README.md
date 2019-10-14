# <h1> Telegram Backup

**tgback** is a program for backing up your [**Telegram**](https://telegram.org) account.

Telegram allows you to restore your account **only through the phone number**, if you lose access to the number
you **can’t get access to your Telegram in any way**.

TelegramBackup(tgback) **creates an endless session of your application** through which in an emergency **you can**
will **change your phone number**, and access your account.

The **.tgback** backup file is encrypted using [**NCv5.1**](https://github.com/NotStatilko/NonCipher)(but you can optionally encrypt as you like) and weighs **only 60 bytes**. You can easily **save** your backup **as a QR** code and print it on paper.

**Your backup is not transferred anywhere.**

# <h2> Installation
You can clone this repository via `git`
```
git clone https://github.com/NotStatilko/tgback
```
Or download `.exe` file direct from my official [**TelegramBackup Channel**](https://t.me/nontgback)
# <h2> Ok, how to?
  
For first you need to create your own application.

1) Go to **https://my.telegram.org** and enter your number there, after, enter the verification string that Telegram will send you.
2) Select **API Development Tools**. You will be taken to the tab of your application.
Please note that the **API ID and the API Hash are secret and shouldn't be shown to anyone**. In the future, these two options will allow **FULL** access to your account. More about this below.

3) Run `tgback.exe` or the `tgback.py` file and select **1 section**
4) **Enter** your **API ID** and **API Hash** and follow the instructions.

After all these operations, you will receive a `.tgback` file. This is your backup file. Session file `.session` can be deleted.

**If you accidentally declassified your API ID and API Hash, go to Active Sessions and terminate your application session.**
Settings -> Privacy and Security -> Active Sessions. **Your application should not be active since backup**, periodically
check it out. If you see something suspicious - **immediately disconnect the session**. After disconnecting, your account will not be
access even if the attacker has the secret parameters of your application.

**Encrypt your backup with a complex password, and everything will be ok!**
