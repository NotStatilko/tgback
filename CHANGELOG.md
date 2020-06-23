# Tgback updates to beta(2.0) of version 3.0!
## What's new?

1. **QR Codes**. Now backups can be saved **as QR codes**, them can be read inside the TelegramBackup. You can even read it from a good quality photo! The QR code is updated along with the backup refresh, and is sent automatically with a welcome message.

<img src="https://telegra.ph/file/d5c76ab1f117bc4bd58fa.jpg" width="" height=""></img>

2. **Reed Solomon codes**. Regular backups are now additionally protected by [Reed Solomon codes](https://en.m.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction). If data is corrupted, they can help. Backup size now takes at least **4 kilobytes**.

3. **Improved encryption**. Now IV is randomly generated and added to the ciphertext. Earlier `TgbackAES` took IV from the password, which is a [**vulnerability**](https://en.m.wikipedia.org/wiki/Initialization_vector).

4. **Improved Keygen**. Earlier, the password was passed in the basis exclusively through the `sha3_256` hash function, which is also a vulnerability because of [ASIC](https://en.m.wikipedia.org/wiki/Application-specific_integrated_circuit) devices. Now, a lot of hash functions are involved in generating the key from the password, and their order completely [depends on the password](https://github.com/NotStatilko/tgback/blob/fb469622ebe658e411c51f09b4cde935d48dce88/tgback_utils.py#L59).

5. **Calls and codes**. Now if you don't receive the code, you can request it again. After several requests to re-send the Telegram code, they will **call you** and dictate it.

6. **Refusal of user's API ID and API Hash**. Previously, the user had to create and provide their own API ID and Hash API, which could be misleading. Hardcoded parameters are now used. This **does not** affect anything, but now it’s enough to provide only a phone number and password. I would ask the developers **not to use them**, but to generate their own. I advise users to download files (including the specified links) **only** from this repository and official [**Telegram Channel**](https://t.me/nontgback).

7. **Minor improvements of navigation and much bugfixes!**


###### _Backups of the new version are not compatible with the old ones, and vice versa. You can still use beta (1.x), but if you have the opportunity, please upgrade to the latest version._
