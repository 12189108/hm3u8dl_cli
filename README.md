# hm3u8dl python m3u8视频下载器

python version ≥ 3.7

## 1 功能介绍

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



## 3 使用

```
pip install --upgrade hm3u8dl_cli
```

```
m3u8download('https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8',title='132')
```

完成下载！

另可参照2中参数摸索使用
