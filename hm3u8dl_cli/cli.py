
from argparse import ArgumentParser

import hm3u8dl_cli
from hm3u8dl_cli import version, m3u8download


def main(argv=None):
    parser = ArgumentParser(
        prog=f"hm3u8dl_cli version {version.version}",
        description=("一个简约、美观、简单的python m3u8视频下载器,支持各类解密,https://github.com/hecoter/hm3u8dl_cli"),
        add_help=False
    )
    parser.add_argument('-h', '--help')
    parser.add_argument("-title", default=None, help="视频名称")
    parser.add_argument("-method", default=None, help='解密方法')
    parser.add_argument("-key", default=None, help='key')
    parser.add_argument("-iv", default=None, help='iv')
    parser.add_argument("-nonce", default=None, help='nonce 可能用到的第二个key')
    parser.add_argument("-enable_del", default=True, help='下载完删除多余文件')
    parser.add_argument("-merge_mode", default=3, type=int,help='1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg合并转码')
    parser.add_argument("-base_uri", default=None, help="解析时的baseuri")
    parser.add_argument("-threads", default=16,type=int,help='线程数')
    parser.add_argument("-headers", default={},help='请求头')
    parser.add_argument("-work_dir", default='./Downloads', help='工作目录')
    parser.add_argument("-proxy", default=None,
                        help="代理：{'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}")

    parser.add_argument("m3u8url", default='', help="m3u8网络链接、本地文件链接、本地文件夹链接、txt文件内容")

    Args = parser.parse_args(argv)
    args1 = hm3u8dl_cli.args()

    args1.m3u8url = Args.m3u8url
    args1.title = Args.title
    args1.method = Args.method
    args1.key = Args.key
    args1.iv = Args.iv
    args1.nonce = Args.nonce
    args1.enable_del = False if Args.enable_del != True else True
    args1.merge_mode = int(Args.merge_mode)
    args1.base_uri = Args.base_uri
    args1.headers = Args.headers
    args1.work_dir = Args.work_dir
    args1.proxy = Args.proxy
    args1.threads = int(Args.threads)

    m3u8download(args1)


if __name__ == '__main__':
    main()