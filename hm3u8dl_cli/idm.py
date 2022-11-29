import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

FILE_SIZE = 0
DONE_SIZE = 0
START_TIME = 0

def calc_divisional_range(filesize, chuck=10):
    step = filesize//chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr)-1):
        s_pos, e_pos = arr[i], arr[i+1]-1
        result.append([s_pos, e_pos])
    result[-1][-1] = filesize-1
    return result

# 下载方法
def range_download(url,save_name, s_pos, e_pos):
    global DONE_SIZE
    global START_TIME
    START_TIME = time.time()
    headers = {"Range": f"bytes={s_pos}-{e_pos}"}
    res = requests.get(url, headers=headers, stream=True)
    with open(save_name, "rb+") as f:
        f.seek(s_pos)
        for chunk in res.iter_content(chunk_size=64*1024):
            if chunk:
                f.write(chunk)
                DONE_SIZE += (e_pos - s_pos)
                # process_bar(all_count=FILE_SIZE, done_count=DONE_SIZE, down_size=DONE_SIZE, start_time=START_TIME)
    START_TIME = 0



def download(url,save_name=None,headers=None):
    global FILE_SIZE
    global START_TIME

    # url = 'http://yue.cmvideo.cn:8080/depository_yqv/asset/zhengshi/5102/598/709/5102598709/media/5102598709_5010999563_56.mp4'
    if save_name is None:
        save_name = url.split('/')[-1]
    print(save_name,'下载中……')
    res = requests.head(url)
    FILE_SIZE = int(res.headers['Content-Length'])

    divisional_ranges = calc_divisional_range(FILE_SIZE)

    # 先创建空文件
    with open(save_name, "wb") as f:
        pass
    with ThreadPoolExecutor() as p:
        futures = []
        for s_pos, e_pos in divisional_ranges:
            # print(s_pos, e_pos)
            futures.append(p.submit(range_download,url,save_name, s_pos, e_pos))
        # 等待所有任务执行完毕
        as_completed(futures)
    print(save_name,'下载完成！')
    return True

if __name__ == '__main__':
    url = input('输入下载链接：') # http://1252524126.vod2.myqcloud.com/9764a7a5vodtransgzp1252524126/80dfa52d5285890812675094126/drm/v.f100230.ts

    download(url)