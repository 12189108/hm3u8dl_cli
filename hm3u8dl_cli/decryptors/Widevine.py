import base64
import subprocess
from hm3u8dl_cli.util import Util


def decrypt(temp_file, key):
    print('Widevine')
    toolsPath = Util().toolsPath()
    try:
        # https://widevine-proxy.appspot.com/proxy
        if key is None:
            key = input('输入key：')
            # 转为hex
        key = Util().toBytes(key).hex()
        before_title = temp_file + '.mp4'
        after_title = temp_file + '_de.mp4'

        command = fr'{toolsPath["mp4decrypt"]} --key 1:{key} "{before_title}" "{after_title}"'

        # 自行下载 mp4decrypt
        subprocess.call(command, shell=True)
        return True

        # Util().delFile(before_title)
    except:
        print('解密出错，请检查key是否正确并配置mp4decrypt \n')
        return False
