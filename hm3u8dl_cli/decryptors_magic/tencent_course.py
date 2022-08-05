
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

def tencent_course(e):
    def aes_decrypt(data, key, iv):
        cryptor = AES.new(key=key.encode(), mode=AES.MODE_CBC, iv=iv.encode())
        dekey = cryptor.decrypt(base64.b64decode(data))
        return unpad(dekey,16).decode()
    return aes_decrypt(base64.b64encode(bytes.fromhex(e[32:-16])).decode(),e[:32],e[-16:])

dsign = 'b489a27096464a94839c17a4e1e4d42c6600ff81e0168e17b33ac363b3d3c4fa0eea09fb23ee162e0532369423c401d89cab47d234724df8'
key = tencent_course(dsign)
print(key)
