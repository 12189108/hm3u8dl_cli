import base64
import sys

from Crypto.Cipher import AES


def decrypt(key:bytes=None,iv:bytes=None,encrypt_ts:bytes=None):
    if iv is None:
        iv = bytes([0]*16)

    cryptor = AES.new(key, mode=AES.MODE_CBC, iv=iv)
    decrypt_ts = cryptor.decrypt(encrypt_ts)
    return decrypt_ts



