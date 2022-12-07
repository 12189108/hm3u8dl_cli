import time
from rich import print
from tqdm import tqdm

from hm3u8dl_cli.util import Util

def process_bar(all_count:int, done_count:int, down_size:int, start_time:float):
    """ 进度条

    :param all_count: ts总数
    :param done_count: 已下载ts数
    :param down_size: 已下载大小
    :param start_time: 下载开始时间
    :return: None
    """
    percent = f'{int(done_count / all_count * 100)}%'.rjust(4)
    end_time = time.time()
    i = int(30 * done_count / all_count)
    done_bar = f'[red]{"━"*i}[/][white]{"━"*(30-i)}[/]'
    rest_bar = f'[yellow][{Util().sizeFormat(down_size)}/{Util().sizeFormat((down_size / done_count) * all_count)}][/]'.ljust(30)
    speed = f'[blue]{Util().sizeFormat(down_size / (end_time - start_time))}/s[/]'.rjust(12)
    try:
        eta = int((end_time - start_time) * (all_count - done_count) / done_count)
    except:
        eta = 0
    eta = f'{time.strftime("%H:%M:%S", time.gmtime(eta))}'.ljust(12)
    print(percent,done_bar,rest_bar,speed,eta,end='\r')


def process_bar_tqdm(all_count:int, done_count:int, down_size:int, start_time:float):
    """ 进度条

    :param all_count: ts总数
    :param done_count: 已下载ts数
    :param down_size: 已下载大小
    :param start_time: 下载开始时间
    :return: None
    """
    with tqdm(total=all_count, desc='Example', leave=False, unit='B', unit_scale=True) as pbar:
        pbar.update(done_count)

