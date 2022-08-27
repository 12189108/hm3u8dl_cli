import re


def decrypt(m3u8url:str) -> str:
    """ xiaoetong 替换链接

    :param m3u8url: 传入m3u8链接
    :return: 不加密的链接
    """
    replace_header = ['encrypt-k-vod.xet.tech']
    true_header = '1252524126.vod2.myqcloud.com'
    for i in replace_header:
        if i in m3u8url:
            m3u8url = m3u8url.replace(i, true_header)

            m3u8url = re.sub('_\d+', '', m3u8url).replace('.ts', '.m3u8')
    return m3u8url

if __name__ == '__main__':
    xet = 'https://encrypt-k-vod.xet.tech/9764a7a5vodtransgzp1252524126/687aeb143701925923896791914/drm/v.f421220.ts?start=0&end=469439&type=mpegts&sign=8537eb05e0adefdd638e5f6a8ba5b2bd&t=630a80e1&us=kOWSVLyfeL'
    url = decrypt(xet)
    print(url)
