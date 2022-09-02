import base64
import json, os, re, sys
import time
import requests, m3u8
from rich.table import Table
from rich.console import Console
from urllib.request import getproxies
from urllib.parse import unquote,quote
from hm3u8dl_cli import util
from hm3u8dl_cli.decryptors import Decrypt, copyrightDRM
from hm3u8dl_cli.decryptors_magic import xet,cctv,drm_getlicense_v1,urlmagic,bokecc,bjcloudvod
from hm3u8dl_cli import tsInfo,download,idm
import hm3u8dl_cli


class args:
    m3u8url = ''
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
    threads = 16
    _ = None



class Parser:  # 解析m3u8内容，返回一大堆信息
    def __init__(self, args):

        self.args = args

        self.args_type = type(args)
        self.tsinfo = None
        self.durations = 0
        self.segments = None
        self.logger = util.Util().createLogger()
        self.m3u8obj = None
        self.temp_dir = None
        self.headers_range = []

    def preload_m3u8url(self):
        # self.args.m3u8url, self.args.key = huke.decrypt(self.args.m3u8url, self.args.key)
        self.args.m3u8url = xet.decrypt(self.args.m3u8url)
        self.args.m3u8url = urlmagic.decrypt(self.args.m3u8url)
        self.args.m3u8url = cctv.decrypt(self.args.m3u8url)
        self.args.m3u8url = bjcloudvod.decrypt(self.args.m3u8url)
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成, {json.dumps(self.args.m3u8url)}')

    def preload_proxy(self):
        """ 尝试使用系统代理，无代理的情况下才会根据输入去确定代理

        :return:
        """
        try:
            self.args.proxy = getproxies()['http']
        except:
            if type(self.args.proxy) == str:
                self.args.proxy = {'http': self.args.proxy}
            elif type(self.args.proxy) == dict:
                self.args.proxy = self.args.proxy
            else:
                self.args.proxy = None

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成, {json.dumps(self.args.proxy)}')

    def preload_headers(self):
        if self.args.headers == {}:
            self.args.headers['user-agent'] = util.Util().randomUA()

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成, {json.dumps(self.args.headers)}')

    def preload_title(self):
        if self.args.title is None:
            self.args.title = util.Util().guessTitle(self.args.m3u8url)
        self.args.title = util.Util().titleFormat(self.args.title)
        if os.path.exists(self.args.work_dir + '/' + self.args.title + '.mp4'):
            self.args.title += '_'
            self.preload_title()

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.args.title)}')

    def preload_toolsPath(self):
        toolsPath = util.Util().toolsPath()
        self.logger.info(
            f'{sys._getframe().f_code.co_name.ljust(20)}  {toolsPath}')
    def preload_work_dir(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            os.makedirs(self.temp_dir + '/video')
        self.logger.info(
            f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,创建文件夹 {self.temp_dir}')

    def preload_m3u8obj(self, m3u8obj):

        def del_privinf(data):
            if '#EXT-X-PRIVINF' in data:
                data = re.sub('#EXT-X-PRIVINF.+', '', data, re.DOTALL)
                return del_privinf(data)
            return data

        if '#EXT-X-PRIVINF:' in m3u8obj.dumps():
            response = requests.get(self.args.m3u8url, verify=False, proxies=self.args.proxy).text
            m3u8data = del_privinf(response)
            with open('temp.m3u8', 'w', encoding='utf-8') as f:
                f.write(m3u8data)
                f.close()
            m3u8obj = m3u8.load('temp.m3u8')
            m3u8obj = self.preload_m3u8obj(m3u8obj)
            util.Util().delFile('temp.m3u8')

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成')
        return m3u8obj

    def preload_base_uri(self):
        if self.m3u8obj.base_uri.count('//') > 1:
            self.m3u8obj.base_uri = '/'.join(self.m3u8obj.base_uri.split('/')[:3])

        if self.args.base_uri is not None:
            self.m3u8obj.base_uri = self.args.base_uri
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.m3u8obj.base_uri)}')

    def preload_method(self):
        if self.args.method != None:  # 自定义method
            pass
        else:  # 自动判断method

            if self.m3u8obj.data['keys'] == []:
                self.args.method = None
            elif self.m3u8obj.data['keys'][-1] is None:
                self.args.method = None

            else:
                self.args.method = self.m3u8obj.data['keys'][-1]['method']
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.args.method)}')

    def preload_key(self):

        if self.args.key is not None:  # 自定义key
            self.args.key = util.Util().toBytes(self.args.key)
        else:
            self.args.key = self.m3u8obj.data['keys'][-1]['uri']

            # 可用的链接
            if type(self.args.key) == str and 'drm.vod2.myqcloud.com/getlicense/v1' in self.args.key:
                self.args.key = drm_getlicense_v1.decrypt(self.args.key)  # 腾讯云解密
            if type(self.args.key) == str and 'bokecc.com' in self.args.key:
                self.args.key = bokecc.decrypt(self.args.key)  # bokecc解密

            self.args.key = util.Util().toBytes(self.args.key)

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{self.args.key}')

    def preload_iv(self):
        if self.args.iv is not None:  # 自定义iv
            self.args.iv = util.Util().toBytes(self.args.iv)
        else:
            if self.m3u8obj.data['keys'] == [None] or self.args.iv is None:
                self.args.iv = bytes([0]*16)
            elif 'iv' in self.m3u8obj.data['keys'][-1]:
                self.args.iv = self.m3u8obj.data['keys'][-1]['iv']
            elif 'keyid' in self.m3u8obj.data['keys'][-1]:
                self.args.iv = self.m3u8obj.data['keys'][-1]['keyid']
            # 可用的链接
            self.args.iv = util.Util().toBytes(self.args.iv)
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{self.args.iv}')

    def preload_nonce(self):
        if self.args.method == 'CHACHA' and self.args.nonce is None:
            self.args.nonce = input('Please input nonce:')
            self.args.nonce = util.Util().toBytes(self.args.nonce)
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.args.nonce)}')

    def preload_tsinfo(self):

        tsurl = self.segments[0]['uri']
        self.args.ts = util.Util().toBytes(tsurl)
        self.args.ts = Decrypt(self.args)
        with open(f'{self.args.work_dir}/{self.args.title}_tsinfo.ts', 'wb') as f:
            f.write(self.args.ts)
            f.close()
        del self.args.ts
        self.tsinfo = tsInfo.tsInfo(f'{self.args.work_dir}/{self.args.title}_tsinfo.ts')

        util.Util().delFile(f'{self.args.work_dir}/{self.args.title}_tsinfo.ts')
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{self.tsinfo}')
        return self.tsinfo

    def listSort(self,List1):
        table = Table()
        console = Console(color_system='256', style=None)
        List2 = []
        if List1 == []:
            print('列表获取错误')
            return
        elif len(List1) == 1:
            return List1
        i = 1
        table.add_column(f'[red]sn')
        table.add_column(f'[red]title')
        table.add_column(f'[red]m3u8url')
        for List in List1:
            table.add_row(
                str(i),
                List['title'],
                List['m3u8url'],
            )
            i = i + 1
        console.print(table)

        numbers = input('输入下载序列（① 5 ② 4-10 ③ 4 10）:')
        if ' ' in numbers:
            for number in numbers.split(' '):
                List2.append(List1[int(number) - 1])
        elif '-' in numbers:
            number = re.findall('\d+', numbers)
            return List1[int(number[0]) - 1:int(number[1])]
        else:
            number = re.findall('\d+', numbers)
            List2.append(List1[int(number[0]) - 1])
            return List2
        return List2

    def type_parseM3u8(self):
        m3u8obj = m3u8.load(quote(self.args.m3u8url, safe=";/?:@&=+$,", encoding="utf-8"), headers=self.args.headers, verify_ssl=False,
                            http_client=m3u8.DefaultHTTPClient(proxies=self.args.proxy))
        self.m3u8obj = self.preload_m3u8obj(m3u8obj)
        with open(self.args.work_dir + '/' + self.args.title + '/' + 'raw.m3u8', 'w', encoding='utf-8') as f:
            f.write(self.m3u8obj.dumps())
        self.preload_base_uri()
        self.segments = self.m3u8obj.data['segments']

        ######################## mastelist
        if self.m3u8obj.data['playlists'] != []:
            infos = []
            print('检测到大师列表，构造链接……')
            playlists = self.m3u8obj.data['playlists']
            for playlist in playlists:
                self.args.m3u8url = self.m3u8obj.base_uri + playlist['uri'] if playlist['uri'][:4] != 'http' else playlist['uri']
                info_temp = {
                    'm3u8url':self.args.m3u8url,
                    'title':self.args.title,
                    'method':self.args.method,
                    'key':self.args.key,
                    'iv':self.args.iv,
                    'nonce':self.args.nonce,
                    'enable_del':self.args.enable_del,
                    'merge_mode':self.args.merge_mode,
                    'base_uri':self.args.base_uri,
                    'headers':self.args.headers,
                    'work_dir':self.args.work_dir,
                    'proxy':self.args.proxy
                }

                infos.append(info_temp)
            if self.m3u8obj.data['media'] != []:
                medias = self.m3u8obj.data['media']

                # self.base_uri_parse = '/'.join(m3u8obj.base_uri.split('/')[:-3])
                for media in medias:
                    self.args.m3u8url = self.m3u8obj.base_uri + media['uri'] if media['uri'][:4] != 'http' else media['uri']

                    info_temp = {
                        'm3u8url': self.args.m3u8url,
                        'title': self.args.title,
                        'method': self.args.method,
                        'key': self.args.key,
                        'iv': self.args.iv,
                        'nonce': self.args.nonce,
                        'enable_del': self.args.enable_del,
                        'merge_mode': self.args.merge_mode,
                        'base_uri': self.args.base_uri,
                        'headers': self.args.headers,
                        'work_dir': self.args.work_dir,
                        'proxy': self.args.proxy
                    }

                    infos.append(info_temp)
            # 加入列表选择
            infos = self.listSort(infos)

            for args1 in infos:

                hm3u8dl_cli.m3u8download(args1)
            return None
        #########################

        self.preload_method()

        if self.args.method:
            self.preload_key()
            self.preload_iv()

            if self.args.method == 'CHACHA':
                self.preload_nonce()
            # wv 视频先下载文件头
            elif self.args.method == 'SAMPLE-AES-CTR':
                init = self.m3u8obj.base_uri + self.segments[0]['init_section']['uri'] if \
                    self.segments[0]['init_section']['uri'][:4] != 'http' else self.segments[0]['init_section']['uri']

                with open(self.temp_dir + '.mp4', 'wb') as f:
                    init_content = requests.get(init).content
                    f.write(init_content)
                    f.close()
                self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} SAMPLE-AES-CTR 文件头下载完成,{init_content}')

            elif self.args.method == 'SAMPLE-AES':
                init = self.segments[0]['init_section']['uri']
                with open(self.temp_dir + '.mp4', 'wb') as f:
                    init_content = requests.get(init).content
                    f.write(init_content)
                    f.close()
                self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} SAMPLE-AES 文件头下载完成,{init_content}')

            elif self.args.method == 'copyrightDRM':
                copyrightDRM.decrypt(self.args.m3u8url,self.args.title,base64.b64encode(self.args.key).decode())
                self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} copyrightDRM 解密完成')
                return None

        for i, segment in enumerate(self.segments):
            # 计算时长
            if 'duration' in segment:
                self.durations += segment['duration']

            if 'byterange' in segment:
                startByte = int(segment['byterange'].split('@')[1])
                expectByte = int(segment['byterange'].split('@')[0])
                self.headers_range.append({
                    'Range':f"bytes={startByte}-{startByte + expectByte}",
                    'User-Agent':util.Util().randomUA()
                }
                )
                # print(f"bytes={startByte}-{startByte + expectByte}")

            # 构造ts链接
            if 'http' != segment['uri'][:4]:
                if segment['uri'][:2] == '//':
                    segment['uri'] = 'https:' + segment['uri']
                else:
                    segment['uri'] = self.m3u8obj.base_uri + segment['uri']

                self.segments[i]['uri'] = segment['uri']
            segment['title'] = str(i).zfill(6)
            self.segments[i]['title'] = segment['title']
            # print(segment)

        self.preload_tsinfo()

        data = json.dumps(self.m3u8obj.data, indent=4, default=str)

        with open(f'{self.args.work_dir}/{self.args.title}/meta.json', 'w', encoding='utf-8') as f:
            f.write(data)

        self.args._ = {
            'tsinfo': self.tsinfo,
            'durations': self.durations,
            'count': len(self.segments),
            'temp_dir': self.temp_dir,
            'segments': self.segments,
            'logger': self.logger,
            'm3u8obj': self.m3u8obj,
            'headers_range':self.headers_range
        }

        return self.args

    def type_parseMPD(self):
        """ mpd 转 m3u8 再进行下载

        :return:
        """
        pass

    def type_parseFile(self):
        idm.download(url=self.args.m3u8url, save_name=self.args.title)
        return None

    def type_parseDir(self):
        for root, dirs, files in os.walk(self.args.m3u8url):
            for f in files:
                file = os.path.join(root, f)
                if os.path.isfile(file):
                    if file.split('.')[-1] == 'm3u8':
                        args1 = args()
                        args1.m3u8url = file
                        hm3u8dl_cli.m3u8download(args1)

        return None
    def type_parseTXT(self):
        with open(self.args.m3u8url,'r',encoding='utf-8') as f:
            txt_contents = f.read()
            f.close()
        contents = txt_contents.split('\n')

        for content in contents:
            args1 = args()
            line = content.split(',')
            args1.title = line[0]
            args1.m3u8url = line[1]
            if len(line) == 3:
                args1.key = line[2]

            hm3u8dl_cli.m3u8download(args1)
        return None
    # @Util().calTime
    def run(self):
        if self.args_type == list:
            args1 = self.args()
            for tempargs in args1:
                print('paraser 313:',tempargs.m3u8url)
                hm3u8dl_cli.m3u8download(tempargs)
            return None
        else:
            self.preload_m3u8url()
            self.preload_proxy()
            self.preload_headers()
            self.preload_title()
            self.preload_toolsPath()
            self.temp_dir = self.args.work_dir + '/' + self.args.title
            self.preload_work_dir()
            # 解析m3u8文件
            if '.mp4' in self.args.m3u8url and 'm3u8' not in self.args.m3u8url:
                self.type_parseFile()
            elif os.path.isdir(self.args.m3u8url):
                return self.type_parseDir()
            elif os.path.isfile(self.args.m3u8url) and self.args.m3u8url.endswith('.txt'):
                return self.type_parseTXT()
            else:
                return self.type_parseM3u8()
