import sys

from .AES_128_CBC import decrypt as AES_128_CBC_decrypt
from .AES_128_ECB import decrypt as AES_128_ECB_decrypt
from .CHACHA import decrypt as CHACHA_decrypt
from .copyrightDRM import decrypt as copyrightDRM_decrypt
from .FakeImage import decrypt as FakeImage_decrypt
from .Widevine import decrypt as Widevine_decrypt


def Decrypt(args2):

    if args2.method is None:
        return FakeImage_decrypt(args2.ts)
    elif args2.method == 'AES-128':
        return AES_128_CBC_decrypt(key=args2.key, iv=args2.iv, encrypt_ts=args2.ts)
    elif args2.method == 'AES-128-ECB':
        return AES_128_ECB_decrypt(key=args2.key, iv=args2.iv, encrypt_ts=args2.ts)
    elif args2.method == 'CHACHA':
        return CHACHA_decrypt(key=args2.key, nonce=args2.nonce, encrypt_ts=args2.ts)
    else:
        return args2.ts
    args2.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成')


