

import base64

def decrypt(url:str):
    prefix =  'bjcloudvod://'
    if url.startswith(prefix):
        url = url[len(prefix):len(url)].replace("-","+").replace("_","/")
        pad = len(url) % 4
        if pad == 2:
            url += "--"
        if pad == 3:
            url += "="
        url = base64.decodebytes(url.encode())
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