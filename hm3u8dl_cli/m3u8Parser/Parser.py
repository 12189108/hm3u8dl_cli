import base64
import json, os, re, sys

import requests, m3u8
from rich.table import Table
from rich.console import Console
from urllib.request import getproxies
from urllib.parse import unquote, quote
from multiprocessing import cpu_count

import hm3u8dl_cli.m3u8download
from hm3u8dl_cli.util import Util,M3U8InfoObj

from hm3u8dl_cli.tsInfo import tsInfo
from hm3u8dl_cli.idm import download as idm_download

from hm3u8dl_cli.decryptors_magic import *
from hm3u8dl_cli.decryptors import Decrypt,copyrightDRM_decrypt


class Parser:  # 解析m3u8内容，返回一大堆信息
    def __init__(self, m3u8InfoObj):

        self.m3u8InfoObj = m3u8InfoObj
        self.m3u8InfoObj._ = None


        self.tsinfo = None
        self.durations = 0
        self.segments = None
        self.logger = Util.createLogger()
        self.m3u8obj = None
        self.temp_dir = None
        self.headers_range = []
        self.m3u8InfoObj_type = type(self.m3u8InfoObj)

    def preload_m3u8url(self):

        # self.m3u8InfoObj.m3u8url = xet_decrypt(self.m3u8InfoObj.m3u8url)
        self.m3u8InfoObj.m3u8url = urlmagic_decrypt(self.m3u8InfoObj.m3u8url)
        self.m3u8InfoObj.m3u8url = cctv_decrypt(self.m3u8InfoObj.m3u8url)
        self.m3u8InfoObj.m3u8url = bjcloudvod_decrypt(self.m3u8InfoObj.m3u8url)
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成, {json.dumps(self.m3u8InfoObj.m3u8url)}')

    def preload_proxy(self):
        """ 尝试使用系统代理，无代理的情况下才会根据输入去确定代理

        :return:
        """
        try:
            self.m3u8InfoObj.proxy = getproxies()['http']
        except:
            if type(self.m3u8InfoObj.proxy) == str:
                self.m3u8InfoObj.proxy = {'http': self.m3u8InfoObj.proxy}
            elif type(self.m3u8InfoObj.proxy) == dict:
                self.m3u8InfoObj.proxy = self.m3u8InfoObj.proxy
            else:
                self.m3u8InfoObj.proxy = None

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成, {json.dumps(self.m3u8InfoObj.proxy)}')

    def preload_headers(self):
        if self.m3u8InfoObj.headers == {}:
            self.m3u8InfoObj.headers['user-agent'] = Util.randomUA()

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成, {json.dumps(self.m3u8InfoObj.headers)}')

    def preload_title(self):
        if self.m3u8InfoObj.title is None:
            self.m3u8InfoObj.title = Util.guessTitle(self.m3u8InfoObj.m3u8url)
        if self.m3u8InfoObj.title.endswith('.mp4'):
            self.m3u8InfoObj.title = self.m3u8InfoObj.title[:-4]
        self.m3u8InfoObj.title = Util.titleFormat(self.m3u8InfoObj.title)
        if os.path.exists(self.m3u8InfoObj.work_dir + '/' + self.m3u8InfoObj.title + '.mp4'):
            self.m3u8InfoObj.title += '_'
            self.preload_title()

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.m3u8InfoObj.title)}')

    def preload_toolsPath(self):
        toolsPath = Util.toolsPath()
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
            response = requests.get(self.m3u8InfoObj.m3u8url, verify=False, proxies=self.m3u8InfoObj.proxy).text
            m3u8data = del_privinf(response)
            with open('temp.m3u8', 'w', encoding='utf-8') as f:
                f.write(m3u8data)
                f.close()
            m3u8obj = m3u8.load('temp.m3u8')
            m3u8obj = self.preload_m3u8obj(m3u8obj)
            Util.delFile('temp.m3u8')

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成')
        return m3u8obj

    def preload_base_uri(self):
        if self.m3u8obj.base_uri.count('//') > 1:
            self.m3u8obj.base_uri = '/'.join(self.m3u8obj.base_uri.split('/')[:3])

        if self.m3u8InfoObj.base_uri is not None:
            self.m3u8obj.base_uri = self.m3u8InfoObj.base_uri

        # 再次检验base_uri
        if self.m3u8obj.base_uri[-1] == '/' and self.m3u8obj.data['segments'] != [] and  self.m3u8obj.data['segments'][0]['uri'][0] == '/':
            self.m3u8obj.base_uri = '/'.join(self.m3u8obj.base_uri.split('/')[:3])

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.m3u8obj.base_uri)}')

    def preload_method(self):
        if self.m3u8InfoObj.method != None:  # 自定义method
            pass
        else:  # 自动判断method

            if self.m3u8obj.data['keys'] == []:
                self.m3u8InfoObj.method = None
            elif self.m3u8obj.data['keys'][-1] is None:
                self.m3u8InfoObj.method = None

            else:
                self.m3u8InfoObj.method = self.m3u8obj.data['keys'][-1]['method']
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.m3u8InfoObj.method)}')

    def preload_key(self):

        if self.m3u8InfoObj.key is not None:  # 自定义key
            self.m3u8InfoObj.key = Util.toBytes(self.m3u8InfoObj.key)
        else:
            self.m3u8InfoObj.key = self.m3u8obj.data['keys'][-1]['uri']


            # 可用的链接
            if type(self.m3u8InfoObj.key) == str and 'drm.vod2.myqcloud.com/getlicense/v1' in self.m3u8InfoObj.key:
                self.m3u8InfoObj.key = drm_getlicense_v1_decrypt(self.m3u8InfoObj.key)  # 腾讯云解密
            elif type(self.m3u8InfoObj.key) == str and 'bokecc.com' in self.m3u8InfoObj.key:
                self.m3u8InfoObj.key = bokecc_decrypt(self.m3u8InfoObj.key)  # bokecc解密
            elif type(self.m3u8InfoObj.key) == str and '.key' in self.m3u8InfoObj.key and not self.m3u8InfoObj.key.startswith('http'):
                self.m3u8InfoObj.key = self.m3u8obj.base_uri + self.m3u8InfoObj.key

            self.m3u8InfoObj.key = Util.toBytes(self.m3u8InfoObj.key)

        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{self.m3u8InfoObj.key}')

    def preload_iv(self):
        if self.m3u8InfoObj.iv is not None:  # 自定义iv
            self.m3u8InfoObj.iv = Util.toBytes(self.m3u8InfoObj.iv)
        else:
            if self.m3u8obj.data['keys'] == [None] or self.m3u8InfoObj.iv is None:
                self.m3u8InfoObj.iv = bytes([0] * 16)
            elif 'iv' in self.m3u8obj.data['keys'][-1]:
                self.m3u8InfoObj.iv = self.m3u8obj.data['keys'][-1]['iv']
            elif 'keyid' in self.m3u8obj.data['keys'][-1]:
                self.m3u8InfoObj.iv = self.m3u8obj.data['keys'][-1]['keyid']
            # 可用的链接
            self.m3u8InfoObj.iv = Util.toBytes(self.m3u8InfoObj.iv)
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{self.m3u8InfoObj.iv}')

    def preload_nonce(self):
        if self.m3u8InfoObj.method == 'CHACHA' and self.m3u8InfoObj.nonce is None:
            self.m3u8InfoObj.nonce = input('Please input nonce:')
            self.m3u8InfoObj.nonce = Util.toBytes(self.m3u8InfoObj.nonce)
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{json.dumps(self.m3u8InfoObj.nonce)}')

    def preload_tsinfo(self):

        tsurl = self.segments[0]['uri']

        self.m3u8InfoObj.ts = Util.toBytes(tsurl, self.m3u8InfoObj.headers)
        self.m3u8InfoObj.ts = Decrypt(self.m3u8InfoObj)

        with open(f'{self.m3u8InfoObj.work_dir}/{self.m3u8InfoObj.title}_tsinfo.ts', 'wb') as f:

            f.write(self.m3u8InfoObj.ts)
            f.close()
        del self.m3u8InfoObj.ts
        self.tsinfo = tsInfo(f'{self.m3u8InfoObj.work_dir}/{self.m3u8InfoObj.title}_tsinfo.ts')

        Util.delFile(f'{self.m3u8InfoObj.work_dir}/{self.m3u8InfoObj.title}_tsinfo.ts')
        self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} 执行完成,{self.tsinfo}')
        return self.tsinfo

    def preload_threads(self):
        if self.m3u8InfoObj.threads is None:
            self.m3u8InfoObj.threads = cpu_count()

    def listSort(self, List1):
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
        if os.path.isfile(self.m3u8InfoObj.m3u8url):
            m3u8obj = m3u8.load(self.m3u8InfoObj.m3u8url, headers=self.m3u8InfoObj.headers,
                                verify_ssl=False,
                                http_client=m3u8.DefaultHTTPClient(proxies=self.m3u8InfoObj.proxy))
        else:


            try:
                m3u8obj = m3u8.load(quote(self.m3u8InfoObj.m3u8url, safe=";/?:@&=+$,", encoding="utf-8"),
                                    headers=self.m3u8InfoObj.headers, verify_ssl=False,
                                    http_client=m3u8.DefaultHTTPClient(proxies=self.m3u8InfoObj.proxy))
            except:
                m3u8content = requests.get(quote(self.m3u8InfoObj.m3u8url, safe=";/?:@&=+$,", encoding="utf-8"),headers=self.m3u8InfoObj.headers, verify=False).text
                # 阿里云method自动判断
                if 'MEATHOD' in m3u8content:
                    self.m3u8InfoObj.method = 'AES-128-ECB'
                m3u8content = m3u8content.replace('#EXT-X-KEY:MEATHOD', '#EXT-X-KEY:METHOD')
                m3u8obj = m3u8.loads(m3u8content, self.m3u8InfoObj.m3u8url)


        self.m3u8obj = self.preload_m3u8obj(m3u8obj)
        with open(self.m3u8InfoObj.work_dir + '/' + self.m3u8InfoObj.title + '/' + 'raw.m3u8', 'w', encoding='utf-8') as f:
            f.write(self.m3u8obj.dumps())
        self.preload_base_uri()
        self.segments = self.m3u8obj.data['segments']

        ######################## mastelist
        if self.m3u8obj.data['playlists'] != []:
            infos = []
            print('检测到大师列表，构造链接……')
            playlists = self.m3u8obj.data['playlists']
            for playlist in playlists:
                self.m3u8InfoObj.m3u8url = self.m3u8obj.base_uri + playlist['uri'] if playlist['uri'][:4] != 'http' else \
                playlist['uri']
                info_temp = {
                    'm3u8url': self.m3u8InfoObj.m3u8url,
                    'title': self.m3u8InfoObj.title,
                    'method': self.m3u8InfoObj.method,
                    'key': self.m3u8InfoObj.key,
                    'iv': self.m3u8InfoObj.iv,
                    'nonce': self.m3u8InfoObj.nonce,
                    'enable_del': self.m3u8InfoObj.enable_del,
                    'merge_mode': self.m3u8InfoObj.merge_mode,
                    'base_uri': self.m3u8InfoObj.base_uri,
                    'headers': self.m3u8InfoObj.headers,
                    'work_dir': self.m3u8InfoObj.work_dir,
                    'proxy': self.m3u8InfoObj.proxy,
                    'server': self.m3u8InfoObj.server,
                    'server_id': self.m3u8InfoObj.server_id,
                }

                infos.append(info_temp)
            if self.m3u8obj.data['media'] != []:
                medias = self.m3u8obj.data['media']

                # self.base_uri_parse = '/'.join(m3u8obj.base_uri.split('/')[:-3])
                for media in medias:
                    self.m3u8InfoObj.m3u8url = self.m3u8obj.base_uri + media['uri'] if media['uri'][:4] != 'http' else media[
                        'uri']

                    info_temp = {
                        'm3u8url': self.m3u8InfoObj.m3u8url,
                        'title': self.m3u8InfoObj.title,
                        'method': self.m3u8InfoObj.method,
                        'key': self.m3u8InfoObj.key,
                        'iv': self.m3u8InfoObj.iv,
                        'nonce': self.m3u8InfoObj.nonce,
                        'enable_del': self.m3u8InfoObj.enable_del,
                        'merge_mode': self.m3u8InfoObj.merge_mode,
                        'base_uri': self.m3u8InfoObj.base_uri,
                        'headers': self.m3u8InfoObj.headers,
                        'work_dir': self.m3u8InfoObj.work_dir,
                        'proxy': self.m3u8InfoObj.proxy,
                        'server': self.m3u8InfoObj.server,
                        'server_id': self.m3u8InfoObj.server_id,
                    }

                    infos.append(info_temp)
            # 加入列表选择
            infos = self.listSort(infos)

            for args1 in infos:
                hm3u8dl_cli.m3u8download(args1)
            return None
        #########################

        self.preload_method()

        if self.m3u8InfoObj.method:
            self.preload_key()
            self.preload_iv()

            if self.m3u8InfoObj.method == 'CHACHA':
                self.preload_nonce()
            # wv 视频先下载文件头
            elif self.m3u8InfoObj.method == 'SAMPLE-AES-CTR':
                init = self.m3u8obj.base_uri + self.segments[0]['init_section']['uri'] if \
                    self.segments[0]['init_section']['uri'][:4] != 'http' else self.segments[0]['init_section']['uri']

                with open(self.temp_dir + '.mp4', 'wb') as f:
                    init_content = requests.get(init).content
                    f.write(init_content)
                    f.close()
                self.logger.info(
                    f'{sys._getframe().f_code.co_name.ljust(20)} SAMPLE-AES-CTR 文件头下载完成,{init_content}')

            elif self.m3u8InfoObj.method == 'SAMPLE-AES':
                init = self.segments[0]['init_section']['uri']
                with open(self.temp_dir + '.mp4', 'wb') as f:
                    init_content = requests.get(init).content
                    f.write(init_content)
                    f.close()
                self.logger.info(f'{sys._getframe().f_code.co_name.ljust(20)} SAMPLE-AES 文件头下载完成,{init_content}')

            elif self.m3u8InfoObj.method == 'copyrightDRM':
                copyrightDRM_decrypt(self.m3u8InfoObj.m3u8url, self.m3u8InfoObj.title, base64.b64encode(self.m3u8InfoObj.key).decode())
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
                    'Range': f"bytes={startByte}-{startByte + expectByte}",
                    'User-Agent': Util.randomUA()
                }
                )
                # print(f"bytes={startByte}-{startByte + expectByte}")

            # 构造ts链接
            if 'http' != segment['uri'][:4]:
                if segment['uri'][:2] == '//':
                    segment['uri'] = 'https:' + segment['uri']
                elif self.m3u8obj.base_uri[-1] == '/' and segment['uri'][0] == '/':
                    self.m3u8obj.base_uri = '/'.join(self.m3u8obj.base_uri.split('/')[:3])
                    segment['uri'] = self.m3u8obj.base_uri + segment['uri']
                else:
                    segment['uri'] = self.m3u8obj.base_uri + segment['uri']

                self.segments[i]['uri'] = segment['uri']

            segment['title'] = str(i).zfill(6)
            self.segments[i]['title'] = segment['title']

        self.preload_tsinfo()

        data = json.dumps(self.m3u8obj.data, indent=4, default=str)

        with open(f'{self.m3u8InfoObj.work_dir}/{self.m3u8InfoObj.title}/meta.json', 'w', encoding='utf-8') as f:
            f.write(data)

        self.m3u8InfoObj._ = {
            'tsinfo': self.tsinfo,
            'durations': self.durations,
            'count': len(self.segments),
            'temp_dir': self.temp_dir,
            'segments': self.segments,
            'logger': self.logger,
            'm3u8obj': self.m3u8obj,
            'headers_range': self.headers_range
        }

        return self.m3u8InfoObj

    def type_parseMPD(self):
        """ mpd 转 m3u8 再进行下载

        :return:
        """
        pass

    def type_parseFile(self):

        status = idm_download(url=self.m3u8InfoObj.m3u8url, save_name=self.m3u8InfoObj.work_dir + '/' + self.m3u8InfoObj.title + '.mp4')
        return None

    def type_parseDir(self):
        for root, dirs, files in os.walk(self.m3u8InfoObj.m3u8url):
            for f in files:
                file = os.path.join(root, f)
                if os.path.isfile(file):
                    if file.split('.')[-1] == 'm3u8':
                        m3u8InfoObj = M3U8InfoObj()
                        m3u8InfoObj.m3u8url = file

                        hm3u8dl_cli.m3u8download(m3u8InfoObj)

        return None

    def type_parseTXT(self):
        with open(self.m3u8InfoObj.m3u8url, 'r', encoding='utf-8') as f:
            txt_contents = f.read()
            f.close()
        contents = txt_contents.split('\n')

        for content in contents:
            try:
                m3u8InfoObj = M3U8InfoObj()
                line = content.split(',')
                m3u8InfoObj.title = line[0]
                m3u8InfoObj.m3u8url = line[1]
                if len(line) == 3:
                    m3u8InfoObj.key = line[2]

                hm3u8dl_cli.m3u8download(m3u8InfoObj)
            except:
                pass
        return None


    def run(self):
        self.preload_m3u8url()
        self.preload_proxy()
        self.preload_headers()
        self.preload_title()
        self.preload_toolsPath()
        self.preload_threads()
        self.temp_dir = self.m3u8InfoObj.work_dir + '/' + self.m3u8InfoObj.title
        self.preload_work_dir()
        # 解析m3u8文件

        if '.mp4' in self.m3u8InfoObj.m3u8url and 'm3u8' not in self.m3u8InfoObj.m3u8url:
            self.type_parseFile()
        elif os.path.isdir(self.m3u8InfoObj.m3u8url):
            return self.type_parseDir()
        elif os.path.isfile(self.m3u8InfoObj.m3u8url) and self.m3u8InfoObj.m3u8url.endswith('.txt'):
            return self.type_parseTXT()
        else:
            return self.type_parseM3u8()
