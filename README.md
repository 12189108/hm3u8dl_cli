# hm3u8dl python m3u8视频下载器

<p align="center">
    <a href="https://img.shields.io/badge/python-%E2%89%A5v3.7-blue" style="text-decoration:none" >
        <img alt="GitHub Python version" src="https://img.shields.io/badge/python-%E2%89%A5v3.7-blue">
    </a>
    <a href="https://github.com/hecoter/hm3u8dl_cli/stargazers" style="text-decoration:none" >
        <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/hecoter/hm3u8dl_cli">
    </a>
    <a href="https://github.com/hecoter/hm3u8dl_cli/network" style="text-decoration:none" >
        <img alt="GitHub forks" src="https://img.shields.io/github/forks/hecoter/hm3u8dl_cli">
    </a>
    <a href="https://github.com/hecoter/hm3u8dl_cli/issues" style="text-decoration:none">
        <img alt="GitHub issues" src="https://img.shields.io/github/issues/hecoter/hm3u8dl_cli">
    </a>
    <a href="https://github.com/hecoter/hm3u8dl_cli/blob/main/LICENSE" style="text-decoration:none" >
        <img alt="GitHub" src="https://img.shields.io/github/license/hecoter/hm3u8dl_cli">
    </a>
</p>


两行代码下载m3u8视频流

视频介绍：

一款功能强大的m3u8下载器 hm3u8dl : https://www.bilibili.com/video/BV1hP4y1975u

<iframe src="//player.bilibili.com/player.html?aid=903264758&bvid=BV1hP4y1975u&cid=911754111&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

## 1 特性

解密类：

1. 支持AES-128-CBC , AES-128-ECB , SAMPLE-AES-CTR , cbcs , SAMPLE-AES，copyrightDRM解密
1. 对部分链接支持魔改，自动出key

实用类：

1. 支持多线程下载，断点续传，自动解密

2. 支持多方式加载m3u8文件：链接、本地文件链接，文件夹

3. 自带ffmpeg 等必要文件，无需配置环境变量

4. 支持master 列表选择

5. 支持日志记录

6. 支持在终端中使用

7. 输出彩色信息，且只有一行，方便批量爬取视频

8. 支持 windows mac linux，全平台通用

9. 支持下载出错自动跳过

10. 随机请求头

11. GUI 版本正在测试

    

## 2 参数介绍

```
必填参数:
  m3u8url      	m3u8网络链接、本地文件链接、本地文件夹链接、txt文件内容

非必填参数:
  -h, --help    show this help message and exit
  -title        视频名称
  -method       解密方法
  -key          key
  -iv           iv
  -nonce        nonce 可能用到的第二个key
  -enable_del	下载完删除多余文件
  -merge_mode	1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg转码
  -base_uri     解析时的baseuri
  -threads      线程数
  -headers      请求头
  -work_dir     工作目录
  -proxy        代理：{'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}
```

## 3 命令行版使用

https://gitee.com/hecoter/hm3u8dl_cli/releases 或 https://github.com/hecoter/hm3u8dl_cli/releases 下载CLI版

在终端中进行调用：

```
.\hm3u8dl_cli_v0.4.9.exe "https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8"
```

```
.\hm3u8dl_cli_v0.4.9.exe "https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8" -title "title"
```

…………

## *4 GUI 版使用*

*不推荐使用*

<img src="https://gitee.com/hecoter/blog/raw/master/imags/QQ%E6%88%AA%E5%9B%BE20221207202346.png" style="zoom:50%;" />

<img src="https://gitee.com/hecoter/blog/raw/master/imags/QQ%E6%88%AA%E5%9B%BE20221207202404.png" style="zoom:50%;" />

<img src="https://gitee.com/hecoter/blog/raw/master/imags/QQ%E6%88%AA%E5%9B%BE20221207202410.png" style="zoom:50%;" />

<img src="https://gitee.com/hecoter/blog/raw/master/imags/0.png" style="zoom:50%;" />

## 5 python 用户使用

安装：

```
pip install --upgrade hm3u8dl_cli
```

使用 1：

```
from hm3u8dl_cli import m3u8download
m3u8download('https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',title='132')
```

使用 2：

```
from hm3u8dl_cli.util import M3U8InfoObj
from hm3u8dl_cli import m3u8download

m3u8InfoObj = M3U8InfoObj() # 示例化一个m3u8Info对象

m3u8InfoObj.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
m3u8InfoObj.title = '标题'

m3u8download(m3u8InfoObj) # 只需填一个参数
```

#### m3u8url 示例（必填）

```
from hm3u8dl_cli import m3u8download
m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8' # 网络链接
# m3u8url = r"C:\Users\hecot\Desktop\m3u8文件夹" # 文件夹
# m3u8url = r"C:\Users\hecot\Downloads\4adf37ccc0342e919fef2de4d02b473a_3 (3).m3u8"  # 本地文件
# m3u8url = r"C:\Users\hecot\Desktop\新建 文本文档.txt" # txt 文件
""" txt 文件内容格式： title,m3u8url,key
文件标题1,C:\Users\hecot\Desktop\m3u8文件夹\1.m3u8
文件标题2,C:\Users\hecot\Desktop\m3u8文件夹\1.m3u8
"""
m3u8download(m3u8url,merge_mode=3)
```

#### title 示例（选填）

```
from hm3u8dl_cli import m3u8download
m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
title = '标题'
m3u8download(m3u8url,title=title)
```

#### method 示例（选填）

一般可自动识别

```
None、AES-128、AES-128-ECB、CHACHA、copyrightDRM、FakeImage、Widevine
```

#### key (选填)

一般可自动识别，用于自定义key

支持base64,hex,字节各类格式

```
from hm3u8dl_cli import m3u8download
m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
key = 'kQ2aSmyG1FDSmzpqTso/0w=='
# key = b'\x91\r\x9aJl\x86\xd4P\xd2\x9b:jN\xca?\xd3'
# key = '910d9a4a6c86d450d29b3a6a4eca3fd3'
m3u8download(m3u8url,key=key)
```

#### iv（选填）

一般可自动识别，用于自定义iv

同Key

#### nonce (选填)

CHACHA 解密需使用此参数，用法同key

#### enable_del（选填）

下载完成后删除多余文件，`bool`型，默认`True`

```
from hm3u8dl_cli import m3u8download
from hm3u8dl_cli.util import M3U8InfoObj

m3u8InfoObj = M3U8InfoObj()

m3u8InfoObj.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
m3u8InfoObj.enable_del = False

m3u8download(m3u8InfoObj)
```

#### merge_mode （选填）

视频合并类型，`int `型

1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg转码

推荐使用3，鉴于你的电脑可能没有配置ffmpeg 环境，因此默认为 1 

FFmpeg 环境配置 : [FFmpeg 环境配置 · Discussion #23 · hecoter/hm3u8dl_cli (github.com)](https://github.com/hecoter/hm3u8dl_cli/discussions/23)

```
from hm3u8dl_cli import m3u8download
from hm3u8dl_cli.util import M3U8InfoObj

m3u8InfoObj = M3U8InfoObj()

m3u8InfoObj.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
m3u8InfoObj.merge_mode = 3

m3u8download(m3u8InfoObj)
```

#### threads (选填)

下载线程数，`int `型,自动读取电脑配置，默认为 cpu核数

#### headers （选填）

请求头，`dict` 型，默认随机请求头

```
from hm3u8dl_cli import m3u8download
from hm3u8dl_cli.util import M3U8InfoObj

m3u8InfoObj = M3U8InfoObj()

m3u8InfoObj.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
m3u8InfoObj.headers = {
    'User-Agent':'iphone',
    'Referer':'https://ntp.msn.cn/',
    'Cookie':None
}
m3u8download(m3u8InfoObj)
```

#### work_dir （选填）

工作目录，默认  ./Downloads 

```
from hm3u8dl_cli import m3u8download
from hm3u8dl_cli.util import M3U8InfoObj

m3u8InfoObj = M3U8InfoObj()

m3u8InfoObj.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
m3u8InfoObj.work_dir = r'C:\Users\hecot\Desktop'

m3u8download(m3u8InfoObj)
```

#### proxy (选填)

代理，`dict` 型，默认使用系统代理

```
from hm3u8dl_cli import m3u8download
from hm3u8dl_cli.util import M3U8InfoObj

m3u8InfoObj = M3U8InfoObj()

m3u8InfoObj.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8'
m3u8InfoObj.proxy = {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080', 'ftp': 'ftp://127.0.0.1:8080'}
# m3u8InfoObj.proxy = {'http': 'http://127.0.0.1:8080', 'https': 'https://127.0.0.1:8080', 'ftp': 'ftp://127.0.0.1:8080'}

m3u8download(m3u8InfoObj)
```
