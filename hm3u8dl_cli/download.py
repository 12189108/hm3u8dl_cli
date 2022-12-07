import json
import os,re,sys
import warnings
import requests
from threading import Thread
from queue import Queue
import time
from tqdm import tqdm

from hm3u8dl_cli.decryptors import Decrypt
from hm3u8dl_cli.util import Util
from hm3u8dl_cli.processBar import process_bar,process_bar_tqdm

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings()

q = Queue(100000)
time_start = time.time()
ALL_COUNT = 0
DONE_COUNT = 0
DONE_SIZE = 0

class FastRequests:
    def __init__(
            self, infos, threads=20):
        self.threads = threads

        global ALL_COUNT
        ALL_COUNT = len(infos)
        self.all_count = len(infos)
        for info in infos:
            q.put(info)

    def run(self):
        global ALL_COUNT, DONE_COUNT, DONE_SIZE, time_start

        for i in range(self.threads):
            t = Consumer()
            t.start()

        # tqdm 版简略进度条
        with tqdm(total=ALL_COUNT, desc='', leave=False, unit=' segments', unit_scale=True,) as pbar:
            while DONE_COUNT < ALL_COUNT:
                current_p = pbar.n
                end_time = time.time()
                speed = f'{Util.sizeFormat(DONE_SIZE / (end_time - time_start))}/s'
                pbar.set_postfix_str(speed)
                pbar.update(DONE_COUNT -current_p)
                time.sleep(0.01)
            pbar.leave = True
            current_p = pbar.n
            pbar.update(ALL_COUNT - current_p)
        # 下载完后初始化缓存信息
        ALL_COUNT = 0
        DONE_COUNT = 0
        DONE_SIZE = 0
        time_start = time.time()


class Consumer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.retry_times = 16

    def run(self):
        while True:
            if q.qsize() == 0:
                break
            self.download(q.get())

    def download(self, info):
        global DONE_SIZE,DONE_COUNT

        class args:
            method = info['method']
            key = info['key']
            iv = info['iv']
            nonce = info['nonce']
            title = info['title']
            link = info['link']
            proxies = info['proxies']
            headers = info['headers']
            server = info['server']
            server_id = info['server_id']
            ts = b''
        if not os.path.exists(args.title):
            for i in range(self.retry_times):
                try:
                    response = requests.get(url=args.link, headers=args.headers,stream=True,timeout=30, verify=False,
                                            proxies=args.proxies,allow_redirects=False)
                    # 适配需重定向才能得到链接的网站
                    if response.status_code == 302:
                        if 'Location' in response.headers:
                            Location_url = response.headers['Location']
                            Location_url = Location_url.replace('///', '//')
                            response = requests.get(url=Location_url, headers=args.headers, stream=True, timeout=30,
                                                    verify=False,
                                                    proxies=args.proxies, allow_redirects=False)


                    args.ts = response.content
                    #################
                    args.ts = Decrypt(args)

                    ######################


                    DONE_SIZE += args.ts.__sizeof__()

                    with open(args.title, 'wb') as f:
                        f.write(args.ts)
                        f.close()

                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException as e:
                    continue
        DONE_COUNT += 1
        # process_bar(ALL_COUNT,DONE_COUNT,DONE_SIZE,time_start)
        # 上传进度信息
        if args.server:
            data = {
                'server_id':args.server_id,
                'method':args.method,
                'ALL_COUNT':ALL_COUNT,
                'DONE_COUNT':DONE_COUNT,
                'DONE_SIZE':DONE_SIZE,
                'time_start':time_start,
            }
            headers = {'Connection': 'close'}
            try:
                requests.post('http://127.0.0.1:8000/process_info', data=json.dumps(data), headers=headers,
                              verify=False, timeout=1)
            except:
                pass




