import os,re,sys
import warnings
import requests
from threading import Thread
from queue import Queue
import time
from hm3u8dl_cli.util import Util
from hm3u8dl_cli.decryptors import Decrypt
from hm3u8dl_cli.processBar import process_bar
warnings.filterwarnings("ignore")
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

        while DONE_COUNT < ALL_COUNT:
            time.sleep(0.01)

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
            ts = b''
        if not os.path.exists(args.title):
            for i in range(self.retry_times):
                try:
                    response = requests.get(url=args.link, headers=args.headers,stream=True,timeout=30, verify=False,
                                            proxies=args.proxies)


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
        process_bar(ALL_COUNT,DONE_COUNT,DONE_SIZE,time_start)


