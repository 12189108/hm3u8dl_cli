import os
import sys
from argparse import ArgumentParser
from rich import print
from hm3u8dl_cli.m3u8Parser import Parser,download_infos
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
    merge_mode = 1
    base_uri = None
    headers = {}
    work_dir = os.path.abspath('') + '/Downloads'
    proxy = None
    threads = 16

def m3u8download(args):
    # 解析
    args1 = Parser.Parser(args=args).run()

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
    Merge(args1._['temp_dir'],merge_mode=args1.merge_mode)
    # 整段解密
    if util.Util().isWidevine(args1.method):
        args1.enable_del = Widevine.decrypt(args1._['temp_dir'],key=args1.key)

    # 删除多余文件
    if args1.enable_del:
        util.Util().delFile(args1._['temp_dir'])
        if util.Util().isWidevine(args1.method):
            util.Util().delFile(args1._['temp_dir'] + '.mp4')

    print()


