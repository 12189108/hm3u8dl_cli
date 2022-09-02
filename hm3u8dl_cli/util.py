import hashlib
import base64
import random
import re,platform,os,subprocess
import sys
import time
import traceback
from ctypes import c_int
from datetime import datetime

import requests
from shutil import rmtree

from rich.console import Console
from rich.table import Table
import logging


class Util:
    def __init__(self):
        pass

    def createLogger(self):
        log_name = rf'./logs/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.log'
        if not os.path.exists('./logs'):
            os.makedirs('logs')
        logging.basicConfig(filename=log_name, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S',
                            level=logging.DEBUG,encoding='utf-8',errors=None)
        logging.info('hm3u8dl LOG 写入')
        return logging.getLogger(__name__)



    def md5(self, text: str) -> str:
        """ md5 加密

        :param text: 文本
        :return: 文本
        """
        md5 = lambda value: hashlib.md5(value.encode('utf-8')).hexdigest()
        return md5(text)

    def rc4(self,key:bytes,msg:bytes) -> bytes:
        """ rc4 加密/解密

        :param key: key
        :param msg: 文本,中文需encode('gbk')
        :return: 字节类型
        """
        class RC4:
            """
            This class implements the RC4 streaming cipher.

            Derived from http://cypherpunks.venona.com/archive/1994/09/msg00304.html
            """

            def __init__(self, key, streaming=False):
                assert (isinstance(key, (bytes, bytearray)))

                # key scheduling
                S = list(range(0x100))
                j = 0
                for i in range(0x100):
                    j = (S[i] + key[i % len(key)] + j) & 0xff
                    S[i], S[j] = S[j], S[i]
                self.S = S

                # in streaming mode, we retain the keystream state between crypt()
                # invocations
                if streaming:
                    self.keystream = self._keystream_generator()
                else:
                    self.keystream = None

            def crypt(self, data: bytes):
                """
                Encrypts/decrypts data (It's the same thing!)
                """
                assert (isinstance(data, (bytes, bytearray)))
                keystream = self.keystream or self._keystream_generator()  # self.keystream or self._keystream_generator()
                return bytes([a ^ b for a, b in zip(data, keystream)])

            def _keystream_generator(self):
                """
                Generator that returns the bytes of keystream
                """
                S = self.S.copy()
                x = y = 0
                while True:
                    x = (x + 1) & 0xff
                    y = (S[x] + y) & 0xff
                    S[x], S[y] = S[y], S[x]
                    i = (S[x] + S[y]) & 0xff
                    yield S[i]
        ciphertext = RC4(key).crypt(msg)
        return ciphertext

    def hashCode(self,str):
        res = c_int(0)
        if not isinstance(str, bytes):
            str = str.encode()
        for i in bytearray(str):
            res = c_int(c_int(res.value * 0x1f).value + i)
        return res.value

    def sizeFormat(self, size, is_disk=False, precision=1):
        """ 文件大小格式化

        :param size:
        :param is_disk:
        :param precision:
        :return: 500MB
        """
        formats = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
        unit = 1000.0 if is_disk else 1024.0
        if not (isinstance(size, float) or isinstance(size, int)):
            raise TypeError('a float number or an integer number is required!')
        if size < 0:
            raise ValueError('number must be non-negative')
        for i in formats:
            size /= unit
            if size < unit:
                return f'{round(size, precision)}{i}'
        return f'{round(size, precision)}{i}'

    def timeFormat(self,eta):
        """时间格式化

        :param eta: 时间
        :return: 00:10:12
        """
        return time.strftime("%H:%M:%S", time.gmtime(eta))

    def titleFormat(self,title:str) -> str:
        """ 格式化视频名称

        :param title:
        :return:
        """
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "", title)  # 替换为下划线
        if new_title[-1] == ' ':
            new_title = new_title[:-1]
            new_title = self.titleFormat(new_title)
        return new_title[-128:] # 最长不能超过255

    def guessTitle(self,url):
        def youku():
            vid = re.findall('vid=(.+?)&', url)[0].replace('%3D', '=')
            parse_url = f'https://ups.youku.com/ups/get.json?vid={vid}&ccode=0532&client_ip=192.168.1.1&client_ts=1652685&utid=zugIG23ivx8CARuB3b823VC%2B'

            response = requests.get(parse_url).json()
            title = response['data']['video']['title']
            return title

        if 'cibntv.net/playlist/m3u8?vid=' in url or 'youku.com/playlist/m3u8?vid=' in url or 'valipl-a10.cp31' in url:
            title = youku()

        else:
            title = url.split('?')[0].split('/')[-1].split('\\')[-1].replace('.m3u8', '')
        return self.titleFormat(title)

    def isWidevine(self,method:str) -> bool:
        """ 判断是否为 Widevine 加密

        :param method: str
        :return: True/False
        """
        WidevineMethod = ['SAMPLE-AES-CTR', 'cbcs', 'SAMPLE-AES']
        if method in WidevineMethod:
            return True
        else:
            return False

    def getPlatform(self):
        return platform.system()

    def toolsPath(self):

        plat_form = self.getPlatform()

        tools_path = {
            'ffmpeg':'',
            'mp4decrypt':'',
            'youkudecrypt':''
        }

        if sys.argv[0].endswith('exe'):
            basePath = os.path.dirname(os.path.realpath(sys.argv[0])).replace('\\', '/')  # 当前路径
        else:
            basePath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])  # python 安装包使用

        mypath = '/Tools/'

        def ffmpegPath():
            cmd = 'ffmpeg'
            ffmpegInfo = subprocess.getstatusoutput(cmd)[1]
            if '不是内部或外部命令' not in ffmpegInfo: # 环境中ffmpeg
                tools_path['ffmpeg'] = 'ffmpeg'
            else:
                tools_path['ffmpeg'] = basePath + mypath + 'ffmpeg.exe' # python脚本


        def mp4decryptPath():
            """
            python 3.10支持
            :return:
            """
            # match plat_form:
            #     case 'Windows':
            #         tools_path['mp4decrypt'] = basePath + mypath + 'mp4decrypt_win.exe'
            #     case 'Linux':
            #         tools_path['mp4decrypt'] = basePath + mypath + 'mp4decrypt_linux'
            #     case 'Mac':
            #         tools_path['mp4decrypt'] = basePath + mypath + 'mp4decrypt_mac'

            if plat_form == 'Windows':
                tools_path['mp4decrypt'] = basePath + mypath + 'mp4decrypt_win.exe'
            elif plat_form == 'Linux':
                tools_path['mp4decrypt'] = basePath + mypath + 'mp4decrypt_linux'
            elif plat_form == 'Mac':
                tools_path['mp4decrypt'] = basePath + mypath + 'mp4decrypt_mac'
        def youkudecryptPath():
            cmd = 'youkudecrypt'
            youkudecryptInfo = subprocess.getstatusoutput(cmd)[1]
            if '不是内部或外部命令' not in youkudecryptInfo:  # 环境中ffmpeg
                tools_path['youkudecrypt'] = 'youkudecrypt'
            else:
                tools_path['youkudecrypt'] = basePath + mypath + 'youkudecrypt.exe'

        ffmpegPath()
        mp4decryptPath()
        youkudecryptPath()

        return tools_path

    def randomUA(self):
        """ 随机请求头

        :return: UA
        """
        USER_AGENTS = [

            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",

            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",

            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",

            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",

            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",

            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",

            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",

            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",

            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",

            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",

            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",

            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",

            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",

            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",

            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",

            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",

            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",

            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",

            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",

            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",

            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",

            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",

            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",

            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",

            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",

            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",

            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",

            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",

            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",

            "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",

            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",

            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",

            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",

            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"

        ]
        return random.choice(USER_AGENTS)

    def delFile(self,temp_dir):
        """ 删除文件/目录

        :param temp_dir: 文件目录
        :return: True/False
        """
        i = 0
        while os.path.exists(temp_dir):
            if os.path.isdir(temp_dir):
                rmtree(temp_dir,ignore_errors=True)
            else:
                os.remove(temp_dir)
            i += 1
            if i >= 10:
                break
        return False if os.path.exists(temp_dir) else True

    def calTime(self,func):
        """ 装饰器 计算函数运行时间

        :param func: 函数
        :return: 函数
        """
        def wrapper(*args, **kwargs):
            startTime = time.time()
            result = func(*args, **kwargs)
            endTime = time.time()
            print(f'{func.__name__} 耗时{endTime - startTime}s')
            return result

        return wrapper

    def safeRun(self,func):
        """ 装饰器 增加下载报错

                :param func: 函数
                :return: 函数
                """

        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
                result = True
            except Exception as e:
                print(e)
                # traceback.print_exc()
                result = False
            return result

        return wrapper


    def toBytes(self,text:str):
        """ 转成字节类型 from base64、hex to bytes

        :param text:
        :return: bytes
        """
        if type(text) == bytes:
            return text
        elif text.endswith('=='):
            return base64.b64decode(text)
        elif text.startswith('0x') and len(text) == 34: # 0x......
            return self.toBytes(text.split('0x')[-1])
        elif os.path.isfile(text):# 本地文件
            with open(text,'rb') as f:
                fileToBytes = f.read()
                f.close()
            return fileToBytes

        elif text.startswith('http'):# 链接
            response = requests.get(text)
            if response.status_code == 200:
                return response.content
            else:
                print('Maybe the key is wrong.')
                return text
        elif len(text) == 32:
            return bytes.fromhex(text)
        elif len(text) == 16:
            return text.encode()
        else:
            return text

    def base64_decode(self,encode):
        """
        解决base64编码结尾缺少=报错的问题
        """
        missing_padding = 4 - len(encode) % 4
        if missing_padding:
            encode += '=' * missing_padding
        decode = base64.b64decode(encode)
        return decode

    def listSort(self, List1):
        """
        传入一个列表，可以包含title、resolution、m3u8url、videotype、duration、videosize、language、method 等参数，返回一个可供选择的列表
        :param List1:
        :return:
        """
        table = Table()
        console = Console(color_system='256', style=None)
        List2 = []
        if List1 == []:
            print('列表获取错误')
            return
        elif len(List1) == 1:
            return List1
        i = 0
        table.add_column(f'[red]序号')
        table.add_column(f'[red]名称')
        table.add_column(f'[red]类型')
        table.add_column(f'[red]分辨率')
        table.add_column(f'[red]时长')
        table.add_column(f'[red]大小')
        table.add_column(f'[red]语言')
        table.add_column(f'[red]加密类型')
        for List in List1:
            # print("{:>3}  {:<30} {:<10}{:<50}".format(i,List['title'],List['resolution'],List['m3u8url']))
            table.add_row(
                str(i),
                None if 'title' not in List else List['title'],
                None if 'videotype' not in List else List['videotype'],
                None if 'resolution' not in List else List['resolution'],
                None if 'duration' not in List else List['duration'],
                None if 'videosize' not in List else List['videosize'],
                None if 'language' not in List else List['language'],
                None if 'method' not in List else List['method'],
            )
            # print('{:^8}'.format(i), List['Title'],List['play_url'])
            i = i + 1
        console.print(table)

        numbers = input('输入下载序列（① 5 ② 4-10 ③ 4 10）:')
        if ' ' in numbers:
            for number in numbers.split(' '):
                number = int(number)
                List2.append(List1[number])
        elif '-' in numbers:
            number = re.findall('\d+', numbers)
            return List1[int(number[0]):int(number[1]) + 1]
        else:
            number = re.findall('\d+', numbers)
            List2.append(List1[int(number[0])])
            return List2
        return List2

if __name__ == '__main__':
    # "C:\Users\happy\Desktop\Downloads\v.f421220\raw.m3u8"
    toolsPath = Util().toolsPath()
    print(toolsPath)

