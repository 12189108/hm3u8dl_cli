import hm3u8dl_cli.internetdownloadmanager as idm


def download(url, save_name=None, headers=None):
    # url = 'http://yue.cmvideo.cn:8080/depository_yqv/asset/zhengshi/5102/598/709/5102598709/media/5102598709_5010999563_56.mp4'

    if save_name is None:
        save_name = url.split('/')[-1]
    pydownloader = idm.Downloader(info=False)

    pydownloader.download(url, save_name)

    return True


if __name__ == '__main__':
    url = input(
        '输入下载链接：')  # http://1252524126.vod2.myqcloud.com/9764a7a5vodtransgzp1252524126/80dfa52d5285890812675094126/drm/v.f100230.ts

    download(url)
