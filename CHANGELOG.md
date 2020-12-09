# TelegramBackup updates to version 3.1!
## What's new?

1. **Destroy option**. Now you can disconnect Telegram session of your backup with **tgback**.

2. **Use without PIL and ZBar**. If your system doesn't support `ZBar` or `PIL` then you can create only `.tgback files`. You still need `qrcode` python package.

3. **Calls for change phone**. In previous version Telegram sends verification codes for changing number only via SMS. Now Telegram can call you.

4. **Change password**. Now you can change password of your backup. Please note that tgback **can't change** password of old backups or backup copies. It only changes password of **current backup** that you opened. If password of your backup was leaked (it's VERY not ok) please use **"Destroy backup"** option.

5. **TelegramDesktop login**. Now you can use your backups to **login into TelegramDesktop**. It's **much** better than [this](https://github.com/NotStatilko/tgback/issues/8) suggestion. You just need to screenshot Telegram's login QR and provide path to screenshot to tgback. Read more about Telegram's login QRs [here](https://core.telegram.org/api/qr-login).

6. **Refusal of "Stay cool"**. Because you can't be uncool.


###### _Backups of the new version are compatible with the old ones backups of tgback v3.0_
