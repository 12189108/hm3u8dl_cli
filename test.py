import base64

def decodeUrl(url):
    prefix =  'bjcloudvod://'
    if ("" == url or url.index(prefix) != 0):
        return "解析失败"
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
    char = ""
    i = 0
    for i in range(len(url)):
        char = url[i]
        step = i % 4 * c + i % 3 + 1
        result.append(chr(char-step))
    return "".join(result)

if __name__ == '__main__':
    url = "bjcloudvod://Tml8g4N1QzxDZ3uGQndxc3hxN4R5cYFvfntweHVxN3CDcDZHTTU9RExmQUZHNT5ESzI8QEllakZ4ZDxCeDI5dEo0OjxKNW1FSzI7cEIyOTqMMHx-gXBpc0J4cnF5cjZARTY7QUY0Oj1zZDpDeWc9QEY3QnB3ZDdySzc6SEw4P0FHZGlETjJuRnVhWkViTHRdims2fIM2"
    s = decodeUrl(url)
    print(s)
