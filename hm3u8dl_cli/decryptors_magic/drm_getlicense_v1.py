import json
import re
import base64

from Crypto.Cipher import AES
from hm3u8dl_cli.util import Util

# https://drm.vod2.myqcloud.com/getlicense/v1?drmType=SimpleAES&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9~eyJ0eXBlIjoiRHJtVG9rZW4iLCJhcHBJZCI6MTMwNTY0Mjk0MywiZmlsZUlkIjoiMzg3NzAyMzAxMjI0Nzc1NDc1IiwiY3VycmVudFRpbWVTdGFtcCI6MTY1NjQ5NjM1MSwiZXhwaXJlVGltZVN0YW1wIjoyMTQ3NDgzNjQ3LCJyYW5kb20iOjMwMzA5MDk1NSwib3ZlcmxheUtleSI6ImQ2MWJjODY3YmZhZDdlYmI4NjFlYjdiNGM3NGIwYjFlIiwib3ZlcmxheUl2IjoiY2M1YmM4MGJjNTY2YzIwM2YxNGU2YzljYmUyZDgyMTIiLCJjaXBoZXJlZE92ZXJsYXlLZXkiOiIiLCJjaXBoZXJlZE92ZXJsYXlJdiI6IiIsImtleUlkIjowLCJzdHJpY3RNb2RlIjowfQ~CzEjjwko66vmvA79371YTRdfP5LBq5GzZF6EuCzf-5w

def decrypt(keyurl):
    if 'drm.vod2.myqcloud.com/getlicense/v1' in keyurl:
        encrypt_key = Util().toBytes(keyurl)
        encrypt_info = re.findall('~(.+?)~',keyurl)[0]

        enc = Util().base64_decode(encrypt_info).decode()

        jObject = json.loads(enc)
        # print(jObject)
        overlayKey = jObject['overlayKey']
        overlayIv = jObject['overlayIv']
        if len(overlayKey) != 32:
            public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC3pDA7GTxOvNbXRGMi9QSIzQEI+EMD1HcUPJSQSFuRkZkWo4VQECuPRg/xVjqwX1yUrHUvGQJsBwTS/6LIcQiSwYsOqf+8TWxGQOJyW46gPPQVzTjNTiUoq435QB0v11lNxvKWBQIZLmacUZ2r1APta7i/MY4Lx9XlZVMZNUdUywIDAQAB"

            return keyurl
        cryptor = AES.new(key=bytes.fromhex(overlayKey), mode=AES.MODE_CBC, iv=bytes.fromhex(overlayIv))

        decryptkey = cryptor.decrypt(encrypt_key)
        return decryptkey
    else:
        return keyurl


