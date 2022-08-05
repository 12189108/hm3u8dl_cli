import sys
from hm3u8dl_cli.decryptors import AES_128_CBC,AES_128_ECB,CHACHA,copyrightDRM,FakeImage,Widevine

def Decrypt(args2):
    match args2.method:
        case None:
            return FakeImage.decrypt(args2.ts)
        case 'AES-128':
            return AES_128_CBC.decrypt(key=args2.key,iv=args2.iv,encrypt_ts=args2.ts)
        case 'AES-128-ECB':
            return AES_128_ECB.decrypt(key=args2.key,iv=args2.iv,encrypt_ts=args2.ts)
        case 'CHACHA':
            return CHACHA.decrypt(key=args2.key, nonce=args2.nonce, encrypt_ts=args2.ts)
        case _:
            return args2.ts
    args2.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成')

