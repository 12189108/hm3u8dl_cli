import sys

from Crypto.Cipher import AES


def decrypt(key: bytes = None, iv: bytes = None, encrypt_ts: bytes = None):
    try:
        cryptor = AES.new(key, mode=AES.MODE_ECB)
        decrypt_ts = cryptor.decrypt(encrypt_ts)
        return decrypt_ts
    except:
        raise 'key error.'



