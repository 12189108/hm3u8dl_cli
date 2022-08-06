
from hm3u8dl_cli import args,m3u8download # 导入包

args1 = args # 实例化一个参数类
args1.m3u8url = 'https://apd-0c13f2c07a4b5475eff3592289859465.v.smtcdns.com/mv.music.tc.qq.com/AXo-Mmfgica14UElx8vKKMeKwe7p_Ax7hnEOv8zqz9Xo/FF06E5309E63A908D47CC8F167D7DA6E5AF3FA44C085FC2D7B06B1291C10638870F5262AFCEE9F973B0C98C8C802B097ZZqqmusic_default/qmmv_0b6bq4aaaaaabuapwe6etfrfjbyaacdqaaca.f9944.m3u8'

m3u8download(args1) # 传入参数类，实现下载