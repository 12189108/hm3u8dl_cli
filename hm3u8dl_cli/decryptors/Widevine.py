import base64
import subprocess
from hm3u8dl_cli.util import Util


def decrypt(temp_file, key):
    print('Widevine 解密')
    try:
        toolsPath = Util.toolsPath()
        while key is None:
            key = input('输入wvkey：')
        # 转为hex
        key = Util.toBytes(key).hex()
        if len(key) != 16:
            raise 'A wrong key.'
        before_title = temp_file + '.mp4'
        after_title = temp_file + '_de.mp4'

        command = fr'{toolsPath["mp4decrypt"]} --key 1:{key} "{before_title}" "{after_title}"'

        # 自行下载 mp4decrypt
        subprocess.call(command, shell=True)
    except:
        print('解密出错，请检查key是否正确并配置mp4decrypt \n')
        return False