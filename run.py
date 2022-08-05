
from hm3u8dl_cli import args,m3u8download # 导入包

args1 = args # 实例化一个参数类
args1.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8' # 重载 m3u8url
args1.key = 'kQ2aSmyG1FDSmzpqTso/0w=='
args1.title = '视频名称' # 重载 title
m3u8download(args1) # 传入参数类，实现下载