
from Crypto.Cipher import AES
import base64


def tencent_course(e):
    def aes_decrypt(data, key, iv):
        cryptor = AES.new(key=key.encode(), mode=AES.MODE_CBC, iv=iv.encode())
        dekey = cryptor.decrypt(base64.b64decode(data))
        return dekey.decode()

    return aes_decrypt(base64.b64encode(bytes.fromhex(e[32:-16])).decode(), e[:32], e[-16:])


dsign = "b40ff3f1b8ff4af6a9d8e483ce26e1c3903eab0e6117d532fa70ed0a2b41d83560fc9ad90270383308ad018076f142c7ad7c4bd6ec1f466e"
key = tencent_course(dsign)
print(key)