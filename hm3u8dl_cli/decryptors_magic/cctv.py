
def decrypt(m3u8url:str):
    baseuri = 'http://hls.cntv.kcdnvip.com'
    replace_baseuri = ['http://dh5.cntv.qcloudcdn.com','https://dh5.cntv.qcloudcdn.com']
    for i in replace_baseuri:
        if i in m3u8url:
            m3u8url = m3u8url.replace(i,baseuri)
            m3u8url = m3u8url.replace('/h5e','')

    return m3u8url

