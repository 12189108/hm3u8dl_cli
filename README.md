# hm3u8dl python m3u8视频下载器

python version ≥ 3.7

## 功能介绍

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

   

## 参数介绍

```
positional arguments:
  m3u8url               m3u8网络链接、本地文件链接、本地文件夹链接、txt文件内容

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
```



### 具体参数介绍

​	0.**m3u8url:** 支持m3u8网络链接、本地文件链接、本地文件夹链接、txt文件内容，这个一个必填内容

示例1—txt文件传入：

```
from hm3u8dl_cli import m3u8download
m3u8url = r"C:\Users\happy\Desktop\1.txt"
m3u8download(m3u8url)
```

​	其中文本内容：

```
"""title,m3u8url,key
1,http://hls.cntv.kcdnvip.com/asp/hls/850/0303000a/3/default/25eb64a95f094a42bbdea5b23ae756f9/850.m3u8
2,https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8
"""
```

示例2—m3u8网络链接：

```
from hm3u8dl_cli import m3u8download
info = {
    'm3u8url':"https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8",
    'title':'视频名称'
}
m3u8download(info)
```

```
from hm3u8dl_cli import m3u8download

info1 = {
    'm3u8url':"https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_3.m3u8",
    'title':'视频1',
    'enable_del':False
}
info2 = {
    'm3u8url':"https://hls.videocc.net/4adf37ccc0/a/4adf37ccc0342e919fef2de4d02b473a_2.m3u8",
    'title':'视频2',
    'threads':32 # 线程数32
}
infos = [info1,info2]
m3u8download(infos)
```

当检测到大师列表时需手动输入下载序列

[![GJgp6.png](https://s1.328888.xyz/2022/08/27/GJgp6.png)](https://imgloc.com/i/GJgp6)

1. **method**:一般自动识别，AES-128-ECB，copyrightDRM 类型可能要自己输入

   ```
   from hm3u8dl_cli import m3u8download
   
   info1 = {
       'm3u8url':"https://***",
       'title':'视频',
       'method':'copyrightDRM'
   }
   
   m3u8download(info1)
   ```

2. **key**:支持网络链接，本地文件链接，base64格式，hex格式

3. **nonce**:一个可能会用到的参数

4. **enable_del**：bool 类型，默认为True

5. **merge_mode**: 1:二进制合并，2：二进制合并完成后用ffmpeg转码，3：用ffmpeg合并转码。默认为 `3`
6. **work_dir**:工作目录，默认 `./Downloads`

7. **proxy**：使用代理，先尝试使用系统代理，无代理的情况下才会根据输入去确定代理

```
from hm3u8dl_cli import m3u8download
info1 = {
    'm3u8url':"https://***",
    'title':'视频',
    'proxy':{'http':'http://127.0.0.1:8888','https:':'https://127.0.0.1:8888'}
}
m3u8download(info1)
```



## 下载安装

### python 用户

```
pip install hm3u8dl_cli
```

命令行使用示例：

```
hm3u8dl_cli "https://hls.videocc.net/672eabf526/c/672eabf526b94a9ea60c3e701be19ddc_1.m3u8" -title "20190213环专公开课-物理污染方向-双层壁隔声重难点解析" -key "ujIQ0DXrmywwwrGSeb/HPg=="
```

![命令行使用示例.png](https://pic.stackoverflow.wiki/uploadImages/58/45/21/130/2022/08/13/10/19/3e55d79c-651d-467b-9164-e501615e7843.png)

### 普通用户

可下载使用编译好的成品，输入以上命令使用，暂无 GUI 版本

[成品下载](https://github.com/hecoter/hm3u8dl_cli/releases)

