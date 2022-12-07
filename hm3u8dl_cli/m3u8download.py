import json
import os
import time

import requests

from .util import Util,M3U8InfoObj
from .m3u8Parser import parse,download_infos
from .merge import Merge

from .decryptors import Widevine_decrypt
import urllib3

urllib3.disable_warnings()

# @Util.safeRun
def m3u8download(
        m3u8url=None,
        title=None,
        method=None,
        key=None,
        iv=None,
        nonce=None,
        enable_del=True,
        merge_mode=3,
        base_uri=None,
        headers={},
        work_dir=os.path.abspath('') + '/Downloads',
        proxy=None,
        threads=None,
        server = False,
        server_id = int(time.time() * 1000)
):
    """

    :param m3u8url: m3u8链接、文件、文件夹路径
    :param title: 视频名称
    :param method: 解密方法 None、AES-128、AES-128-ECB、CHACHA、copyrightDRM、FakeImage、Widevine
    :param key: 支持base64、hex、字节格式
    :param iv: 支持base64、hex、字节格式
    :param nonce: 支持base64、hex格式
    :param enable_del: True/False
    :param merge_mode: 1/2/3
    :param base_uri:
    :param headers: dict格式，{}
    :param work_dir:
    :param proxy: {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080', 'ftp': 'ftp://127.0.0.1:8080'}
    :param threads: 系统cpu核数
    :return: False/True
    """
    m3u8InfoObj = M3U8InfoObj()
    if type(m3u8url) is dict:
        m3u8InfoObj.m3u8url = m3u8url['m3u8url']
        m3u8InfoObj.title = m3u8url['title']
        m3u8InfoObj.method = m3u8url['method']
        m3u8InfoObj.proxy = m3u8url['proxy']
        m3u8InfoObj.key = m3u8url['key']
        m3u8InfoObj.iv = m3u8url['iv']
        m3u8InfoObj.nonce = m3u8url['nonce']
        m3u8InfoObj.enable_del = m3u8url['enable_del']
        m3u8InfoObj.merge_mode = m3u8url['merge_mode']
        m3u8InfoObj.base_uri = m3u8url['base_uri']
        m3u8InfoObj.headers = m3u8url['headers']
        m3u8InfoObj.work_dir = m3u8url['work_dir']
        m3u8InfoObj.server = m3u8url['server']
        m3u8InfoObj.server_id = m3u8url['server_id']
    elif type(m3u8url) is M3U8InfoObj:
        m3u8InfoObj = m3u8url
    else:
        m3u8InfoObj.m3u8url = m3u8url
        m3u8InfoObj.title = title
        m3u8InfoObj.method = method
        m3u8InfoObj.key = key
        m3u8InfoObj.iv = iv
        m3u8InfoObj.nonce = nonce
        m3u8InfoObj.enable_del = enable_del
        m3u8InfoObj.merge_mode = merge_mode
        m3u8InfoObj.base_uri = base_uri
        m3u8InfoObj.headers = headers
        m3u8InfoObj.work_dir = work_dir
        m3u8InfoObj.proxy = proxy
        m3u8InfoObj.threads = threads
        m3u8InfoObj.server = server
        m3u8InfoObj.server_id = server_id

    if not Util.checkVersion():
        raise 'The python version must be 3.9 or greater.'
    if not isinstance(m3u8InfoObj,M3U8InfoObj):
        raise 'Incorrect input format, not m3u8InfoObj object.'

    m3u8InfoObj = parse(m3u8InfoObj).run()

    if isinstance(m3u8InfoObj,M3U8InfoObj):
        print(
            m3u8InfoObj.title,
            Util.timeFormat(m3u8InfoObj._['durations']),
            m3u8InfoObj.method,
            m3u8InfoObj._['tsinfo']['tsinfo']
        )
        #上传信息
        if m3u8InfoObj.server:
            data = {
                'server_id':m3u8InfoObj.server_id,
                'title':m3u8InfoObj.title,
                'm3u8url':m3u8InfoObj.m3u8url,
                'method':m3u8InfoObj.method,
                'tsinfo':m3u8InfoObj._['tsinfo'],
                'durations':Util.timeFormat(m3u8InfoObj._['durations']),
                'END':False
            }
            headers = {'Connection': 'close'}
            try:
                requests.post('http://127.0.0.1:8000/basic_info', data=json.dumps(data), headers=headers, verify=False,
                              timeout=1)
            except:
                pass


        # download
        download_infos(m3u8InfoObj)
        print()
        # merge
        Merge(m3u8InfoObj._['temp_dir'], merge_mode=m3u8InfoObj.merge_mode)
        # 整段解密
        if Util.isWidevine(m3u8InfoObj.method):
            m3u8InfoObj.enable_del = Widevine_decrypt(m3u8InfoObj._['temp_dir'], key=m3u8InfoObj.key)
        # 删除多余文件
        if m3u8InfoObj.enable_del:
            if os.path.exists(m3u8InfoObj._['temp_dir'] + '.mp4'):
                Util.delFile(m3u8InfoObj._['temp_dir'])
            if Util.isWidevine(m3u8InfoObj.method):
                Util.delFile(m3u8InfoObj._['temp_dir'] + '.mp4')
        if os.path.exists(m3u8InfoObj._['temp_dir'] + '.mp4'):
            END = True
        else:
            END = False
        # 上传信息
        if m3u8InfoObj.server:
            data = {
                'server_id': m3u8InfoObj.server_id,
                'END': END
            }
            headers = {'Connection': 'close'}
            try:
                requests.post('http://127.0.0.1:8000/basic_info', data=json.dumps(data), headers=headers,
                              verify=False,
                              timeout=1)
            except:
                pass
        return END








