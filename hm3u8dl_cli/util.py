import hashlib
import base64
import random
import re, platform, os, subprocess
import sys
import time
import traceback
from ctypes import c_int
from datetime import datetime
from Crypto.Cipher import AES

import requests
from urllib import parse
from shutil import rmtree


from rich.console import Console
from rich.table import Table
import logging


class M3U8InfoObj:
    m3u8url = None
    title = None
    method = None
    key = None
    iv = None
    nonce = None
    enable_del = True
    merge_mode = 3
    base_uri = None
    headers = {}
    work_dir = os.path.abspath('') + '/Downloads'
    proxy = None
    threads = None  # cpu_count()  # 用cpu核数限制协程任务数
    server = False
    server_id = int(time.time() *1000) # 当前视频唯一标志符


class Util:

    @classmethod
    def createLogger(cls):
        log_name = rf'./logs/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.log'
        if not os.path.exists('./logs'):
            os.makedirs('logs')
        logging.basicConfig(filename=log_name, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S',
                            level=logging.DEBUG)
        logging.info('hm3u8dl LOG 写入')
        return logging.getLogger(__name__)

    @classmethod
    def md5(cls, text: str) -> str:
        """ md5 加密

        :param text: 文本
        :return: 文本
        """
        md5 = lambda value: hashlib.md5(value.encode('utf-8')).hexdigest()
        return md5(text)

    @classmethod
    def rc4(cls, key: bytes, msg: bytes) -> bytes:
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

    @classmethod
    def hashCode(cls, str):
        res = c_int(0)
        if not isinstance(str, bytes):
            str = str.encode()
        for i in bytearray(str):
            res = c_int(c_int(res.value * 0x1f).value + i)
        return res.value

    @classmethod
    def sizeFormat(cls, size, is_disk=False, precision=1):
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

    @classmethod
    def timeFormat(cls, eta):
        """时间格式化

        :param eta: 时间
        :return: 00:10:12
        """
        return time.strftime("%H:%M:%S", time.gmtime(eta))

    @classmethod
    def titleFormat(cls, title: str) -> str:
        """ 格式化视频名称

        :param title:
        :return:
        """
        rstr = r"[\/\\\:\*\?\"\<\>\|]》《"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "", title)  # 替换为下划线
        if new_title[-1] == ' ':
            try:
                new_title = new_title[:-1]
                new_title = cls.titleFormat(new_title)
            except:
                new_title = ''
        return new_title[-128:]  # 最长不能超过255

    @classmethod
    def guessTitle(cls, url):
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
        return cls.titleFormat(title)

    @classmethod
    def isWidevine(cls, method: str) -> bool:
        """ 判断是否为 Widevine 加密

        :param method: str
        :return: True/False
        """
        WidevineMethod = ['SAMPLE-AES-CTR', 'cbcs', 'SAMPLE-AES']
        if method in WidevineMethod:
            return True
        else:
            return False

    @classmethod
    def getPlatform(cls):
        return platform.system()

    @classmethod
    def toolsPath(cls):

        plat_form = cls.getPlatform()

        tools_path = {
            'ffmpeg': '',
            'mp4decrypt': '',
            'youkudecrypt': ''
        }

        if sys.argv[0].endswith('exe'):
            basePath = os.path.dirname(os.path.realpath(sys.argv[0])).replace('\\', '/')  # 当前路径
        else:
            basePath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])  # python 安装包使用

        mypath = '/Tools/'

        def ffmpegPath():
            cmd = 'ffmpeg'
            ffmpegInfo = subprocess.getstatusoutput(cmd)[1]

            if '不是内部或外部命令' not in ffmpegInfo:  # 环境中ffmpeg
                tools_path['ffmpeg'] = 'ffmpeg'
            else:
                tools_path['ffmpeg'] = basePath + mypath + 'ffmpeg.exe'  # python脚本

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

    @classmethod
    def randomUA(cls):
        """ 随机请求头

        :return: UA
        """
        USER_AGENTS = [

            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",

            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",

            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",

            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",

            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",

            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",


            "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",

            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",

            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"

        ]
        return random.choice(USER_AGENTS)

    @classmethod
    def delFile(cls, temp_dir):
        """ 删除文件/目录

        :param temp_dir: 文件目录
        :return: True/False
        """
        i = 0
        while os.path.exists(temp_dir):
            if os.path.isdir(temp_dir):
                rmtree(temp_dir, ignore_errors=True)
            else:
                os.remove(temp_dir)
            i += 1
            if i >= 10:
                break
        return False if os.path.exists(temp_dir) else True

    @classmethod
    def calTime(cls, func):
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
    @classmethod
    def safeRun(cls,func):
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
                traceback.print_exc()
                result = False
            return result

        return wrapper


    @classmethod
    def toBytes(cls, text: str, headers=None):
        """ 转成字节类型 from base64、hex to bytes

        :param headers:
        :param text:
        :return: bytes
        """
        if type(text) == bytes:
            return text
        elif text.endswith('=='):
            return base64.b64decode(text)
        elif text.startswith('0x') and len(text) == 34:  # 0x......
            return cls.toBytes(text.split('0x')[-1])
        elif os.path.isfile(text):  # 本地文件
            with open(text, 'rb') as f:
                fileToBytes = f.read()
                f.close()
            return fileToBytes

        elif text.startswith('http'):  # 链接
            text = parse.unquote(text)
            response = requests.get(text, headers=headers, allow_redirects=False,timeout=5)
            if response.status_code == 200:
                return response.content
            elif response.status_code == 302:
                if 'Location' in response.headers:
                    Location_url = response.headers['Location']
                    Location_url = Location_url.replace('///', '//')
                    return cls.toBytes(Location_url, headers=headers)
                else:
                    return text
            else:
                print('Maybe the key is wrong.')
                return text
        elif len(text) == 32:
            return bytes.fromhex(text)
        elif len(text) == 16:
            return text.encode()
        else:
            return text

    @classmethod
    def base64_decode(cls, encode):
        """
        解决base64编码结尾缺少=报错的问题
        """
        missing_padding = 4 - len(encode) % 4
        if missing_padding:
            encode += '=' * missing_padding
        decode = base64.b64decode(encode)
        return decode

    @classmethod
    def listSort(cls, List1):
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

    @classmethod
    def checkVersion(cls):
        # 判断Python版本
        if sys.version_info >= (3, 7):
            return True
        else:
            return False

    @classmethod
    def checkVideo(cls,videoFilePath,fastCheck=True):
        ffmpegPath = cls.toolsPath()['ffmpeg']
        if fastCheck:
            cmd = f'{ffmpegPath} -i "{videoFilePath}" -c copy -f null echo'
        else:
            cmd = f'{ffmpegPath} -i "{videoFilePath}" -f null echo'
        return_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for next_line in return_info.stdout:
            return_line = next_line.decode("utf-8", "ignore")
            print(return_line,end='') # 逐行输出

    @classmethod
    def formatConvert(cls,inputFilePath,outputFilePath):
        with open(inputFilePath,'rb') as f:
            inputFile = f.read()
        status = False
        def ev1ToMp4():
            pass
        def qsvToMp4():
            pass
        def kuxToMp4():
            pass
        def qlvToMp4():
            pass
        if os.path.exists(outputFilePath):
            status = True
        return status

    @classmethod
    def extractAudio(cls,inputFilePath):
        # ffmpeg -i sample.mp4 -q:a 0 -map a sample.mp3
        ffmpegPath = cls.toolsPath()['ffmpeg']
        outputFilePath = ''.join(inputFilePath.split('.')[:-1]) + '.mp3'
        cmd = f'{ffmpegPath} -i {inputFilePath} -q:a 0 -map a {outputFilePath}'
        subprocess.call(cmd,shell=True)

    @classmethod
    def getThumbPic(cls,inputFilePath):
        ffmpegPath = cls.toolsPath()['ffmpeg']
        outputFilePath = ''.join(inputFilePath.split('.')[:-1]) + '.png'
        if os.path.exists(outputFilePath):
            return outputFilePath
        cmd = f'{ffmpegPath} -i {inputFilePath} -vf  "thumbnail,scale=720:480" -frames:v 1 {outputFilePath} -loglevel panic /y'
        subprocess.call(cmd, shell=True)
        return outputFilePath

    @classmethod
    def aliPlayAuth(cls,n, rand, plaintext):
        """
        u = "xef236F94768RwQ6"
        rand = "yX5+nuBMJMvR08ZkA3zd3Uj4XvcZ6CHuyxPAW59V0yw="
        plaintext = "wLTLZbDLkE+SYTyBrJTVgoNiiZ99L7HLmsbYs8Jkqjg="
        """
        unpad = lambda s: s[0:-s[-1]]

        key_iv = cls.md5(n)[8:24].encode('utf-8')
        cryptor = AES.new(key_iv, AES.MODE_CBC, key_iv)
        key = cryptor.decrypt(base64.b64decode(re.sub(r'[\r\n]', '', rand, 0, re.I)))
        cryptor = AES.new(cls.md5(n + str(unpad(key).decode('utf-8')))[8:24].encode('utf-8'), AES.MODE_CBC, key_iv)

        return unpad(cryptor.decrypt(base64.b64decode(plaintext))).decode('utf-8')

    @classmethod
    def extractPES(cls,tsFileContent:bytes):
        """ 抽取PES
        """

        # 初始化空列表用于存放pes
        pes_list = []

        # 逐行读取ts文件
        for line in tsFileContent.split(b'\n'):
            # 使用正则表达式查找pes包
            match = re.search(b'\x00\x00\x01\xE0', line)
            if match:
                # 找到pes包，将其加入列表
                pes_list.append(line)
        # b'\n'.join(pes_list)
        return pes_list


if __name__ == '__main__':
    with open(r"C:\Users\hecot\Desktop\Downloads\v.f220\video\000024.ts",'rb') as f:
        tsFileContent = f.read()
    pes_list = Util.extractPES(tsFileContent)
    print(pes_list[0])
