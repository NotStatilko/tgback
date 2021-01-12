# TelegramBackup v3.1
######  _Don't forget to look at [changelog](CHANGELOG.md)!_

**TelegramBackup** — console application created to backup Telegram accounts. Due to the features of Telegram, you will **not be able** to log into your account if you lose access to the phone number. **Tgback** provides the ability to create an _alternative session_ (as if you were logging in from another device) and restore account with TelegramDesktop or change the number on which the account is linked.

**TelegramBackup** produces a special `.tgback` file as well as a QR code - both are your backup. You can choose what is more convenient for you to store, as `.tgback` and a QR code represent **the same** session. For encryption of backups, `AES-CBC-256` is used with a key in the form of your password passed through more than 2 million hash operations of various hash functions, the order of which is based on the password you set. It's like [**NonHashpass**](https://github.com/NotStatilko/NonHashpass), but another algorithm.

 ## Download and setting
 ### Windows
  It's no executable for Windows for now because i destroyed this piece of ... you know. I will publish executable as soon as I have access to the Windows. Please check official [tgback channel](https://t.me/nontgback). It can be already here (check last commits).
 ### Linux and making Windows executable
  If you want to make **TelegramBackup** then you need to install all dependencies. For the program to work correctly, you need to have [Python 3.6+](https://python.org), [ZBar](http://zbar.sourceforge.net) and [pip](https://pypi.org/project/pip/) (it can be already installed with Python 3.6+, type `pip` or `pip3` in your terminal/cmd). After that, run:
  ```bash
  git clone https://github.com/NotStatilko/tgback; cd tgback
  pip3 install -r requirements.txt || pip install -r requirements.txt
  python3 TelegramBackup.py || python TelegramBackup.py
  ```
  If you want to make executable on Linux or Windows then install `pyinstaller`
  ```
  pip3 install pyinstaller || pip install pyinstaller
  ```
  Go to `tgback/pyinstaller` folder and run
  ```
  pyinstaller TelegramBackup.spec
  ```
  You will need to enter path to tgback folder, just copy it from folder info. After making TelegramBackup executable check it if it works and after  that you can remove all tgback-related stuff (ZBar [if you not on linux], Python, etc).
 
 #### Linux
 If you want to use tgback on Linux then to QR-features you need to have **libzbar0** (or analogue) onto your machine.
 ```
 sudo apt install libzbar0
 ```
 
 ## Backup creation
  To create a backup you need to select **first mode**

  ![main page](https://telegra.ph/file/e36fad83651ef88e38c0f.png)

  And choose the way you will create it.

  ![backup](https://telegra.ph/file/6cec875d76ccfb88fdff7.png)

  You can enter everything manually, or create a special `tgback-config` file. If the first method is inconvenient for you, create a text file and fill it out using this template:
  ```
  phone_number; telegram_password; backup_password; backup_filename
  ```
  Next, you will need to enter the code that Telegram will send you. If this doesn't happen, then you can request the code again. After three attempts, Telegram will **call you** and the robot will dictate it.

  ![request_code](https://telegra.ph/file/119791ec5e3e0a31fed6d.png)

After all operations, you will receive a QR code and `.tgback` file. Please **check your backups** for validity for first.

## Backup refresh and number replacement
 Due to discovered [problem](https://github.com/NotStatilko/tgback/issues/2) backups need to be updated periodically, so that the session doesn't turn off automatically due to inactivity. At the moment once every two months. We can probably increase it to six months, but testing is needed.

**TelegramBackup** automatically creates a reminder message, so you will be notified a week before the deadline. You can refresh the backup and change the number in the mode under number **2**. After refreshing the backup, you will receive a new updated QR code and `.tgback` file. Old backups will remain working, but they will be show the wrong amount of time before the expiration of the validity period.

## A bit about security
 The backups you created **shouldn't** be active since the last update. If you notice something suspicious – **immediately** disconnect (via Destroy option or Telegram) your backup session. After disconnecting a session, **ALL** backups that are attached to it **will be destroyed**.

TelegramBackup backups store **the key to the session**, upon receipt of which the attacker will receive **FULL** control over your account. You must choose complex passwords.

Also, no security audits have been conducted by competent people, so I **do not guarantee** complete cryptographic strength. If you have any suggestions, open issue. I am attaching a QR-backup of my account here, try to hack it if you want!

<img src="https://telegra.ph/file/4309aba93c6d673470e9e.png" width="200" height="200"></img>

## Involved libraries
1. [**Telethon**](https://github.com/LonamiWebs/Telethon) (MIT License)
2. [**Pillow**](https://github.com/python-pillow/Pillow) (PIL Software License)
3. [**PyAES**](https://github.com/ricmoo/pyaes) (MIT License)
4. [**ReedSolomon**](https://github.com/tomerfiliba/reedsolomon) (MIT License)
5. [**PyZBar**](https://github.com/NaturalHistoryMuseum/pyzbar) (MIT License)
6. [**python-qrcode**](https://github.com/lincolnloop/python-qrcode) ([LICENSE](https://github.com/lincolnloop/python-qrcode/blob/master/LICENSE))
7. [**libzbar64.dll**](https://github.com/dani4/ZBarWin64) (GNU LESSER GENERAL PUBLIC LICENSE)
## Donation
If you somehow find this useful —
```
Bitcoin: 1AJxszajUZVard5NEvct9KbC5pCfBBHmt3
```

