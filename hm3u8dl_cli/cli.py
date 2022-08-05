
from argparse import ArgumentParser
from hm3u8dl_cli import util, version, m3u8download


def main(argv=None):
    parser = ArgumentParser(
        prog=f"version {version.version}",
        description=("一个简约、美观、简单的python m3u8视频下载器,支持各类解密,https://github.com/hecoter/hm3u8dl")
    )

    parser.add_argument("m3u8url", default='', help="链接、本地文件链接、文件夹链接")
    parser.add_argument("-title", default=None, help="视频名称")
    parser.add_argument("-method", default=None, help='解密方法')
    parser.add_argument("-key", default=None, help='key')
    parser.add_argument("-iv", default=None, help='iv')
    parser.add_argument("-nonce", default=None, help='nonce 可能用到的第二个key')
    parser.add_argument("-enable_del", default=True, help='下载完删除多余文件')
    parser.add_argument("-merge_mode", default=1, help='1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg转码')
    parser.add_argument("-base_uri", default=None, help="解析时的baseuri")
    parser.add_argument("-threads", default=16, help='线程数')
    parser.add_argument("-headers", default={}, help='请求头')
    parser.add_argument("-work_dir", default='./Downloads', help='工作目录')
    parser.add_argument("-proxy", default=None,
                        help="代理：{'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}")

    Args = parser.parse_args(argv)

    if Args.m3u8url == '':
        pass
    else:
        class args:
            m3u8url = Args.m3u8url
            title = Args.title
            method = Args.method
            key = Args.key
            iv = Args.iv
            nonce = Args.nonce
            enable_del = False if Args.enable_del != True else True
            merge_mode = int(Args.merge_mode)
            base_uri = Args.base_uri
            headers = Args.headers
            work_dir = Args.work_dir
            proxy = Args.proxy
            threads = int(Args.threads)

        m3u8download(args)


if __name__ == '__main__':
    main()