
from hm3u8dl_cli import args,m3u8download # 导入包

args1 = args # 实例化一个参数类
args1.m3u8url = 'https://hls.videocc.net/672eabf526/c/672eabf526b94a9ea60c3e701be19ddc_1.m3u8'
args1.key = 'ujIQ0DXrmywwwrGSeb/HPg=='
args1.title = '20190213环专公开课-物理污染方向-双层壁隔声重难点解析'
m3u8download(args1) # 传入参数类，实现下载