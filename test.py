import time
import m3u8
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


def get_live_url(cid, platform='h5'):
    playUrl = 'https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl'
    params = {
        'cid': cid,  # cid序列号
        'qn': 150,  # 播放的视频质量
        'platform': platform,  # 视频的播放形式
        'ptype': 16
    }
    response = requests.get(playUrl, headers=headers, params=params).json()
    text = response['data']['durl']
    url = text[-1]['url']
    return url


def get_real_url(url):
    playlist = m3u8.load(uri=url, headers=headers)
    print(playlist.playlists)
    return playlist.playlists[0].absolute_uri


def download_video(url, max_count=20, max_size=120*1024*1024):
    max_id = None
    size = 0
    for i in range(1, max_count+1):
        playlist = m3u8.load(uri=url, headers=headers)
        for seg in playlist.segments:
            current_id = int(seg.uri[1:seg.uri.find(".")])
            if max_id and current_id <= max_id:
                continue
            with open("combine.mp4", "ab" if max_id else "wb") as f:
                r = requests.get(seg.absolute_uri, headers=headers)
                data = r.content
                size += len(data)
                f.write(data)
                print(
                    f"\r下载次数({i}/{max_count})，已下载：{size/1024/1024:.2f}MB", end="")
                if size >= max_size:
                    print("\n文件已经超过大小限制，下载结束！")
                    return
        max_id = current_id
        time.sleep(2)


url = get_live_url('22907643')
# real_url = get_real_url(url)
real_url = 'https://d1--cn-gotcha208.bilivideo.com/live-bvc/239375/live_3949941_65651866_1500/index.m3u8?expires=1660224557&len=0&oi=976033154&pt=web&qn=0&trid=1007cd250a9827094d008f816f4889ba1ad0&sigparams=cdn,expires,len,oi,pt,qn,trid&cdn=cn-gotcha208&sign=e538dbdde31ade7d7236f19b0860a9f6&sk=c9c6154426932efa80d25af02e87a3bd&p2p_type=1&src=57345&sl=6&free_type=0&pp=rtmp&machinezone=jd&source=onetier&site=7fcc79d403f6c2399812c4ddc77f6971&order=1'
download_video(real_url)
