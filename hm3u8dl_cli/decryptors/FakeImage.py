

def decrypt(encrypt_ts:bytes=None):
    """ 伪图片解密

    :param encrypt_ts:
    :return:
    """
    if encrypt_ts[:4] == b'\x89PNG' or encrypt_ts[:2] == bytes.fromhex('424D') or encrypt_ts[:2] == bytes.fromhex('FFD8'):
        ts_start = encrypt_ts.find(b'G@')
        decrypt_ts = encrypt_ts[ts_start:]
        return decrypt_ts
    else:
        return encrypt_ts
