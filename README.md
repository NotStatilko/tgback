# TelegramBackup v5.1
######  _Don't forget to look at [changelog](CHANGELOG.md)!_

**TelegramBackup** — console application created to backup Telegram accounts. Due to the features of Telegram you will be **not able** to log into your account if you lose access to the phone number (SIM card). **TGBACK** provides the ability to create an _alternative session_ (as if you were logging in from another device) and get login code or change the number on which the account is linked.

**TelegramBackup** produces a special `.tgback` file as well as a QR code - both are your backup. You can choose what is more convenient for you to store, as `.tgback` and a QR code represent **the same** session. For encryption of backups, **AES-256-CBC** is used with a [scrypt](https://en.wikipedia.org/wiki/Scrypt) key.

 ## Download & Install
 ### Windows
 You can download builds from the [Releases](https://github.com/NotStatilko/tgback/releases) or from official [TGBACK Channel](https://t.me/nontgback).

 ### Linux and making Windows executable
  If you want to make a **TelegramBackup** app then you need to install all dependencies. For the program to work correctly, you need to have [Python 3.7+](https://python.org), [ZBar](http://zbar.sourceforge.net) (for QR features, you may ignore it) and [pip](https://pypi.org/project/pip/) (it can be already installed with Python 3.7+, type `pip` or `pip3` in your terminal/cmd). After that, run:
  ```bash
  # You can install TGBACK from PIP
  pip install tgback[QR] # Not a Pure-python, with QR
  # pip install tgback # Pure-python, no QR support
  ```
  ```bash
  # Or install from GitHub with GIT by cloning repository
  git clone https://github.com/NotStatilko/tgback
  pip install ./tgback[QR] # Not a Pure-python, with QR
  # pip install ./tgback # Pure-python, no QR support
  ```
  ```bash
  tgback # Run installed TGBACK app
  ```
  If you want to make executable on Linux or Windows then install `pyinstaller`
  ```
  pip install pyinstaller
  ```
  Go to `tgback/pyinstaller` (you should clone repo from GitHub) folder and run
  ```
  pyinstaller TelegramBackup.spec
  ```
  After making TelegramBackup executable check it if it works and after that you can remove all tgback-related stuff (ZBar [if you not on linux], Python, etc).

 #### Linux
 If you want to use tgback on Linux with QR-features then you will need to have a **libzbar0** (or analogue) onto your machine.
 ```
 # Debian OS / Ubuntu OS
 sudo apt install libzbar0
 ```
 ## Backup creation
  To create a backup you need to select **first mode**

  ![main page](https://telegra.ph/file/6752f5bf19b5d3a85fb95.png)

  And choose the way you will create it.

  ![backup](https://telegra.ph/file/dc68092c6f80ba0084206.png)

  You can enter everything manually, or create a special `tgback-config` file. If the first method is inconvenient for you, create a text file and fill it out using this template:
  ```
  phone_number; telegram_password; backup_password; backup_filename
  ```
  Next, you will need to enter the code that Telegram will send you. If this doesn't happen, then you can request the code again. After three attempts, Telegram will **call you** and the robot will dictate it.

  ![requestcode](https://telegra.ph/file/45ab9f776fdc84632e64b.png)

After all operations, you will receive a QR code and `.tgback` file. Please **check your backups** for validity for first.

## Backup refresh and number replacement
 Due to discovered [problem](https://github.com/NotStatilko/tgback/issues/2) backups need to be updated periodically, so that the session doesn't turn off automatically due to inactivity. At the moment once every three months. We can probably increase it to five, but testing is needed.

**TelegramBackup** automatically creates a reminder message, so you will be notified a week before the deadline. You can refresh the backup and change the number in the mode under number **2**. After refreshing the backup, you will receive a new updated QR code and `.tgback` file. Old backups will remain working, but they will be show the wrong amount of time before the expiration.

## A bit about security
 The backups you created **shouldn't** be active since the last update. If you notice something suspicious – **immediately** disconnect (via Destroy option or Telegram) your backup session. After disconnecting a session, **ALL** backups that are attached to it **will be inacessible**.

TelegramBackup backups store **session**, upon receipt of which the attacker will receive **FULL** control over your account. Use complex passwords.

Also, no security audits have been conducted by competent people, so I **do not guarantee** complete cryptographic strength. If you have any suggestions, open issue. I am attaching a QR-backup of my account here, try to hack it if you want!

<img src="https://telegra.ph/file/59469cef320ecff9364f8.png" width="300" height="300"></img>

## Involved libraries
1. [**Telethon**](https://github.com/LonamiWebs/Telethon) (MIT License)
2. [**Pillow**](https://github.com/python-pillow/Pillow) (PIL Software License)
3. [**PyAES**](https://github.com/ricmoo/pyaes) (MIT License)
4. [**PyZBar**](https://github.com/NaturalHistoryMuseum/pyzbar) (MIT License)
5. [**python-qrcode**](https://github.com/lincolnloop/python-qrcode) ([LICENSE](https://github.com/lincolnloop/python-qrcode/blob/master/LICENSE))
