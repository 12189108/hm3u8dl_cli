import json
import os
from rich import print

import hm3u8dl_cli
from hm3u8dl_cli.m3u8Parser import Parser, download_infos
from hm3u8dl_cli import util, version
from hm3u8dl_cli.merge import Merge
from hm3u8dl_cli.decryptors import Widevine


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


@hm3u8dl_cli.util.Util().safeRun
def m3u8download(args, **kwargs):
    """ 实际开始解析下载部分

    :param args: 传入一个类或字典
    :return: None
    """
    if type(args) == type or type(args) == hm3u8dl_cli.m3u8Parser.Parser.args or type(args) == hm3u8dl_cli.args:
        pass
    elif type(args) == dict:
        args1 = hm3u8dl_cli.args()
        args1.m3u8url = args['m3u8url']
        args1.title = args1.title if 'title' not in args else args['title']
        args1.method = args1.method if 'method' not in args else args['method']
        args1.key = args1.key if 'key' not in args else args['key']
        args1.iv = args1.iv if 'iv' not in args else args['iv']
        args1.nonce = args1.nonce if 'nonce' not in args else args['nonce']
        args1.enable_del = args1.enable_del if 'enable_del' not in args else args['enable_del']
        args1.merge_mode = args1.merge_mode if 'merge_mode' not in args else args['merge_mode']
        args1.base_uri = args1.base_uri if 'base_uri' not in args else args['base_uri']
        args1.headers = args1.headers if 'headers' not in args else args['headers']
        args1.work_dir = args1.work_dir if 'work_dir' not in args else args['work_dir']
        args1.proxy = args1.proxy if 'proxy' not in args else args['proxy']
        args1.threads = args1.threads if 'threads' not in args else args['threads']
        args = args1

    elif type(args) == list:
        for arg in args:
            m3u8download(arg)
        return

    elif type(args) == str:
        if '{' in args and '}' in args:
            try:
                # 字符串转字典
                arg = json.loads(args)
                m3u8download(arg)
                return
            except:
                pass

        # 纯m3u8url,不推荐
        info = {
            'm3u8url': args
        }
        m3u8download(info)
        return

    else:
        print('不支持的输入格式，请查阅使用文档 https://github.com/hecoter/hm3u8dl_cli')
        return

    # 解析
    args1 = Parser.Parser(args=args).run()

    if args1 is None:
        pass
    else:
        # try:
        #     args1 = Parser.Parser(args=args).run()
        # except Exception as e:
        #     print('error:', e, e.__traceback__.tb_frame.f_globals['__file__'], e.__traceback__.tb_lineno)
        #     sys.exit()
        print(
            args1.title,
            util.Util().timeFormat(args1._['durations']),
            args1.method,
            args1._['tsinfo']
        )
        # 下载
        download_infos.download_infos(args1)
        # 合并
        Merge(args1._['temp_dir'], merge_mode=args1.merge_mode)
        # 整段解密
        if util.Util().isWidevine(args1.method):
            args1.enable_del = Widevine.decrypt(args1._['temp_dir'], key=args1.key)

        # 删除多余文件
        if args1.enable_del:
            if os.path.exists(args1._['temp_dir'] + '.mp4'):
                util.Util().delFile(args1._['temp_dir'])
            if util.Util().isWidevine(args1.method):
                util.Util().delFile(args1._['temp_dir'] + '.mp4')
    print()
