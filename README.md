# TelegramBackup v3.0 beta(2.2)
######  _Don't forget to look at [changelog](CHANGELOG.md)!_

**TelegramBackup** — console application created to backup Telegram accounts. Due to the features of Telegram, you will **not be able** to log into your account if you lose access to the phone number. **Tgback** provides the ability to create an _alternative session_ (as if you were logging in from another device) and change the number on which the account is linked.

**TelegramBackup** produces a special `.tgback` file as well as a QR code - both are your backup. You can choose what is more convenient for you to store, as `.tgback` and a QR code represent **the same** session. For encryption of backups, `AES-CBC-256` is used with a key in the form of your password passed through more than 2 million hash operations of various hash functions, the order of which is based on the password you set.

 ## Download and setting
 ### Windows
  You can download `.exe` file [**from Telegram**](https://t.me/nontgback) or [**from Google Drive**](https://drive.google.com/folderview?id=1-x6Yxp3s5-SOAHTvCHdxkAsYP011jsDz).
 ### Linux
  If you are outside of Windows and want to use **TelegramBackup** - you need to install all dependencies. For the program to work correctly, you need to have [Python 3.6+](https://python.org), [ZBar](http://zbar.sourceforge.net) and after that, run
  ```bash
  git clone https://github.com/NotStatilko/tgback
  cd tgback
  pip install -r requirements.txt
  python TelegramBackup.py
  ```
 ## Backup creation
  To create a backup you need to select **first mode**

  ![main page](https://telegra.ph/file/5ba889aff30a503e32f80.png)

  And choose the way you will create it.

  ![backup](https://telegra.ph/file/0424f7419d2cb13ceffbd.png)

  You can enter everything manually, or create a special `tgback-config` file. If the first method is inconvenient for you, create a text file and fill it out using this template:
  ```
  phone_number; telegram_password; backup_password; backup_filename
  ```
  Next, you will need to enter the code that Telegram will send you. If this doesn't happen, then you can request the code again. After three attempts, Telegram will **call you** and the robot will dictate it.

  ![request_code](https://telegra.ph/file/af75b96c5cab656ed7a89.png)

After all operations, you will receive a QR code and `.tgback` file. Please **check your backups** first for validity, since TelegramBackup is still in beta phase.

## Backup refresh and number replacement
 Due to recently discovered [problem](https://github.com/NotStatilko/tgback/issues/2), which prompted me to sit down for a code rewrite, backups need to be updated periodically, so that the session doesn't turn off automatically due to inactivity. At the moment once every two months. We can probably increase it to six months, but testing is needed.

**TelegramBackup** automatically creates a reminder message, so you will be notified a week before the deadline. You can refresh the backup and change the number in the mode under number **2**. After refreshing the backup, you will receive a new updated QR code and `.tgback` file. Old backups will remain working, but they will show the wrong amount of time before the expiration of the validity period.

## A bit about security
 The backups you created **shouldn't** be active since the last update. If you notice something suspicious – **immediately** disconnect your backup session. After disconnecting a session, backups that are attached to it **will be destroyed**.

Although TelegramBackup allows you to change only the phone number, the backups themselves store **the key to the session**, upon receipt of which the attacker will receive **FULL** control over your account. You must choose complex passwords.

Also, no security audits have been conducted by competent people, so I **do not guarantee** complete cryptographic strength. If you have any comments, open issue. I am attaching a QR-backup of my account here, try to hack if you want!

<img src="https://telegra.ph/file/4309aba93c6d673470e9e.png" width="200" height="200"></img>

## Involved libraries
1. [**Telethon**](https://github.com/LonamiWebs/Telethon) (MIT License)
2. [**Pillow**](https://github.com/python-pillow/Pillow) (PIL Software License)
3. [**PyAES**](https://github.com/ricmoo/pyaes) (MIT License)
4. [**ReedSolomon**](https://github.com/tomerfiliba/reedsolomon) (MIT License)
5. [**PyZBar**](https://github.com/NaturalHistoryMuseum/pyzbar) (MIT License)
6. [**python-qrcode**](https://github.com/lincolnloop/python-qrcode) ([LICENSE](https://github.com/lincolnloop/python-qrcode/blob/master/LICENSE))
7. [**libzbar64.dll**](https://github.com/dani4/ZBarWin64) (GNU LESSER GENERAL PUBLIC LICENSE)
## Bitcoin
If you somehow find this useful —

<img src="https://telegra.ph/file/fdf5512c31826ca738ba8.png" width="200" height="200"></img>
```
1NN4AU6XrECh8WSM2joZ6tRVDcTZyTkzTi
```
