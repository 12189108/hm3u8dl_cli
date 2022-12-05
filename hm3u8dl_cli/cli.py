
from argparse import ArgumentParser
from hm3u8dl_cli.version import version
from hm3u8dl_cli.m3u8download import m3u8download
from hm3u8dl_cli.util import M3U8InfoObj


def main(argv=None):
    parser = ArgumentParser(
        prog=f"hm3u8dl_cli version {version}",
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
    m3u8InfoObj = M3U8InfoObj()

    m3u8InfoObj.m3u8url = Args.m3u8url
    m3u8InfoObj.title = Args.title
    m3u8InfoObj.method = Args.method
    m3u8InfoObj.key = Args.key
    m3u8InfoObj.iv = Args.iv
    m3u8InfoObj.nonce = Args.nonce
    m3u8InfoObj.enable_del = False if Args.enable_del != True else True
    m3u8InfoObj.merge_mode = int(Args.merge_mode)
    m3u8InfoObj.base_uri = Args.base_uri
    m3u8InfoObj.headers = Args.headers
    m3u8InfoObj.work_dir = Args.work_dir
    m3u8InfoObj.proxy = Args.proxy
    m3u8InfoObj.threads = int(Args.threads)

    m3u8download(m3u8InfoObj)


if __name__ == '__main__':
    main()