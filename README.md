# WechatWordCloud
Generating word clouds for WeChat message records.

## To do list
### 1. Get your wechat message database

If you are using iOS device, then you can simply acquire all your message without any encryption by syncing your iphone data to your computer.

On contraire, android and PC users will have encrypted files, and there's some way to crack then, but I can't make it clear in github, for it maybe dangerous for the users.
#### From iOS
Make an uncrypted backup, read the backup file by using some third-party softwares, then you can find the files in usr/documents/tencent.xin/ or something like that(I forgot the exact directory).

#### From Win PC
The typical directory is Documents/Wechat Files/ where you would find a series of sqlite db files with AES32 encryption. You need to crack the database to get your message. The key to the db is hidden in function createFileW when launching wechat and sending "request to login" signal(Please use softwares like x32dbg).

#### From Android
Still discovering...

### 2. Find the sqlite database files and then run the code in the same directory.


## Some tips:

### 1. Do not change the file name of the code easily!
Changing the file name of the code without doing any alternation in the code itself would raise some error in detecting the working directory, I'm still working on solving that problem.

### 2. FOR WIN USERS: Remember to put Chinese font file in your working directory.
And change corresponding code in line 220 and 159 (index not yet updated, find them in adjacent lines) to your desired font. Of course you can simply use your system font directory.


## About Copyrights and Usage (IMPORTANT)
### DO NOT use it in any commercial activity unless it is authorized by me, namely github user LeoAokma. You can definitely use it for fun, but mind that you have to notice me if you are going to quote this project in your academic paper, course project and other educational and academic usage that needs citation.
