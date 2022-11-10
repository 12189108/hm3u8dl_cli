

""" 项目简介
本项目使用requests爬取m3u8链接，并用aiohttp异步下载
"""

from hm3u8dl_cli import m3u8download
m3u8download('https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',title='132')
