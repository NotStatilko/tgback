# <h1> Telegram Backup

**tgback** is a program for backing up your [**Telegram**](https://telegram.org) account.

Telegram allows you to restore your account only through the phone number, if you lose access to the number
you **can’t get access to your Telegram in any way**.

TelegramBackup(tgback) creates an **endless session** of your application through which in an emergency you can
change your phone number, and access your account.

The **.etgback** backup file is encrypted using [AES-256 CBC](https://github.com/ricmoo/pyaes) and weighs **only 1 kilobyte**. You can easily save your backup **as a QR** code and print it on paper.

**Your backup is not transferred anywhere.**

# <h2> Installation

At the moment needed testing. You can wait for stable version and release or clone the repository for yourself and run `TelegramBackup.py`
```
git clone https://github.com/NotStatilko/tgback
```
I **do not** recommend using `tgback2.0` because of many errors.

# <h2> Ok, how to backup?
  
For first you need to create your own application.

1) Go to **https://my.telegram.org** and enter your number there, after, enter the verification string that Telegram will send you.
2) Select **API Development Tools**. You will be taken to the tab of your application.
Please note that the **API ID and the API Hash are secret and shouldn't be shown to anyone**. In the future, these two options will allow **FULL** access to your account. More about this below.

3) Run `TelegramBackup.py` file and select **1 section**
4) **Enter** your **API ID**, **API Hash** and follow the instructions.

After all these operations, you will receive a `.etgback` file. This is **encrypted** by your password backup file.

**If you accidentally declassified password for your backup, go to Active Sessions/Devices and terminate application session.**
`Settings -> Privacy and Security -> Active Sessions`. **Your application should not be active since backup or update**, periodically
check it out. If you see something suspicious - **immediately disconnect the session**. After disconnecting, your account will not be
access even if the attacker has password for your backup.

To maintain a session, necessary to sometimes refresh it. At the moment, i don’t know the limit for inactive sessions, so for now a backup update needed **every two months**. TelegramBackup v3.0 supports this.
