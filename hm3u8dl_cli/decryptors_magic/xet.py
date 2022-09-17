import re


def decrypt(m3u8url:str) -> str:
    """ xiaoetong 替换链接

    :param m3u8url: 传入m3u8/ts链接
    :return: 不加密的链接
    """
    replace_header = ['encrypt-k-vod.xet.tech','1252524126.vod2.myqcloud.com']
    # true_header = '1252524126.vod2.myqcloud.com'
    true_header = 'live-video-tx.xiaoeknow.com'
    for i in replace_header:
        if i in m3u8url:
            m3u8url = m3u8url.replace(i, true_header)
            m3u8url = re.sub('_\d+', '', m3u8url).replace('.ts', '.m3u8').split('?')[0]
    return m3u8url

if __name__ == '__main__':
    xet = 'https://encrypt-k-vod.xet.tech/9764a7a5vodtransgzp1252524126/13d95cb7387702291278183167/drm/v.f421220_0.ts?start=130288&end=288975&type=mpegts&sign=147fba4ebc73602b9ef549104ba8db91&t=63253860&us=OTlkmGwrPD&whref=appwanciwpy7977.pc.xiaoe-tech.com'
    url = decrypt(xet)
    print(url)
