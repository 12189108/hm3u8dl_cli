hm3u8dl python m3u8视频下载器
=============================

这是一个测试版本，python 版本≥3.10

功能介绍
--------

解密类：

1. 支持AES-128-CBC , AES-128-ECB , SAMPLE-AES-CTR , cbcs ,
   SAMPLE-AES，copyrightDRM解密

2. 对部分链接支持魔改，自动出key

实用类：

1. 支持多线程下载，断点续传，自动解密

2. 支持多方式加载m3u8文件：链接、本地文件链接，文件夹

3. 自带ffmpeg 等必要文件，无需配置环境变量

4. 支持master 列表选择

5. 支持日志记录

6. 支持在终端中使用

7. 输出彩色信息，且只有一行，方便批量爬取视频

8. 支持 windows mac linux，全平台通用

参数介绍
--------

.. code:: 

   positional arguments:
     m3u8url               链接、本地文件链接、文件夹链接

   options:
     -h, --help            show this help message and exit
     -title TITLE          视频名称
     -method METHOD        解密方法
     -key KEY              key
     -iv IV                iv
     -nonce NONCE          nonce 可能用到的第二个key
     -enable_del ENABLE_DEL
                           下载完删除多余文件
     -merge_mode MERGE_MODE
                           1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg转码
     -base_uri BASE_URI    解析时的baseuri
     -threads THREADS      线程数
     -headers HEADERS      请求头
     -work_dir WORK_DIR    工作目录
     -proxy PROXY          代理：{'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}

使用方式-高级篇
---------------

准备：

1）安装python,版本≥3.10
https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe

2) 终端输入 ``pip install hm3u8dl_cli`` 安装此包

pycharm 中使用
~~~~~~~~~~~~~~

.. code:: 

   from hm3u8dl_cli import args,m3u8download # 导入包

   args1 = args # 实例化一个参数类
   args1.m3u8url = 'https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8' # 重载 m3u8url
   args1.title = '视频名称' # 重载 title
   m3u8download(args1) # 传入参数类，实现下载

|image1|

终端中使用
~~~~~~~~~~

在终端中输入命令

.. code:: 

   hm3u8dl_cli.exe "https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8" -title "视频名称" -key "kQ2aSmyG1FDSmzpqTso/0w=="

|image2|

使用方式-小白篇
---------------

下载成品文件，输入命令下载

.. |image1| image:: https://s1.328888.xyz/2022/08/06/u6NDy.png
   :target: https://imgloc.com/i/u6NDy
.. |image2| image:: https://s1.328888.xyz/2022/08/06/u6466.png
   :target: https://imgloc.com/i/u6466
