

import base64


def base64_decode(encode):
    """
    解决base64编码结尾缺少=报错的问题
    """
    missing_padding = 4 - len(encode) % 4
    if missing_padding:
        encode += '=' * missing_padding
    decode = base64.b64decode(encode)
    return decode

def decrypt(url:str):
    prefix =  'bjcloudvod://'
    if url.startswith(prefix):
        url = url[len(prefix):len(url)].replace("-","+").replace("_","/")
        url = base64_decode(url)
        factor = url[0]
        c = factor % 8

        url = url[1:len(url)]
        result = []
        for i in range(len(url)):
            char = url[i]
            step = i % 4 * c + i % 3 + 1
            result.append(chr(char-step))
        return "".join(result)
    else:
        return url



if __name__ == '__main__':
    url = 'bjcloudvod://UWl3eXR1PjI0Z3Z8M3dsaWlxMnpqcXxlb3trbmZxMmZ0cDFlZ2I2aTkzNDk7ZDk5a2Q3Zj1oZzU5aGQ5ZzQ8Zjs5PDI7NjVmazc3ZzMyNDB9MHd0cnBkaTN4bWdqcjE1Ojg1ODczOTtkNTg0OmM5Ojw7aDU3M2M6NmJpN2YzajU3OWQ9bGQ8OTlhR0c9Rkw4UE9icnQ2MzQ5OjQ3OTI4PWM0OjM5ZTg5PjpnNzYyZTk1ZGg2aDJpNzY4ZjxrZjs4O2BGSTxFTjdPUWFqNHh9Ng'
    deurl = decrypt(url)
    print(deurl)