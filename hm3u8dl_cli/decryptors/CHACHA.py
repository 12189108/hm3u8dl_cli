from Crypto.Cipher import ChaCha20


def decrypt(key:bytes=None,nonce:bytes=None,encrypt_ts:bytes=None):
    decrypt_ts = b''
    try:
        if len(nonce) != 8:
            print('error:length of nonce must be 8.')
        for i in range(0, len(encrypt_ts), 1024):
            cipher = ChaCha20.new(key=key, nonce=nonce)
            decrypt_ts += cipher.decrypt(encrypt_ts[i:i + 1024])
        return decrypt_ts
    except:
        raise 'key error.'

