import requests
from Crypto.Cipher import AES
import base64

m3u8url = 'https://cd15-ccd1-2.play.bokecc.com/flvs/4066F9F39D08AB88/2022-08-01/E6083C59D62346630498CE5AAF1F53F5-10.m3u8?t=1659757704&key=6A647F060B6E3B350C061B94CCFF96A7&tpl=10&tpt=112' # 重载 m3u8url
keyurl = 'https://p.bokecc.com/servlet/hlskey?info=E6083C59D62346630498CE5AAF1F53F5&t=1659757704&key=83FD7D69CFC49EC5DC87A8633A834AB9'

headers = {
    'User-Agent':'ipad'
}
response = requests.get(keyurl,headers=headers).content

print(len(response))