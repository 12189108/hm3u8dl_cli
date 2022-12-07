import requests

def decrypt(keyurl:str):
    """ bokecc key解密

    :param keyurl:
    :return:
    """
    if 'bokecc.com' in keyurl:
        headers = {
            'User-Agent': 'ipad'
        }
        key = requests.get(keyurl, headers=headers).content
        if len(key) == 16:
            return key
        else:
            return keyurl
    else:
        return keyurl
