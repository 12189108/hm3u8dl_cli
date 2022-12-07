import subprocess
from hm3u8dl_cli.util import Util


def decrypt(m3u8url,title,key):
    toolsPath = Util().toolsPath()
    youkudecryptPath = toolsPath['youkudecrypt']
    cmd = fr'{youkudecryptPath} "{m3u8url}" --workDir "Downloads" --saveName "{title}" --useKeyBase64 "{key}" --enableMuxFastStart --enableYouKuAes --enableDelAfterDone'
    print(cmd)
    # "m3u8url" --workDir "Downloads" --saveName "title" --useKeyBase64 "youkukey" --enableMuxFastStart --enableYouKuAes
    subprocess.call(cmd,shell=True)