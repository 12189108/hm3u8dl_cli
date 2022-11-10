import re
import subprocess

from hm3u8dl_cli.util import Util


def tsInfo(tsPath):
    try:
        ffmpegPath = Util.toolsPath()['ffmpeg']
        cmd = f'{ffmpegPath} -i {tsPath}'

        videoInfo = subprocess.getstatusoutput(cmd)[1]

        bitrate = re.findall('bitrate:(.+?)\n', videoInfo, re.DOTALL)[0]

        try:
            resolution = re.findall('Stream(.+?)\n', videoInfo, re.DOTALL)[0].split(',')[-5:]
        except:
            resolution = ''

        infos = f'bitrate:{bitrate},' + ','.join(resolution)
        return infos
    except Exception as e:
        # print('error:',e,e.__traceback__.tb_frame.f_globals['__file__'],e.__traceback__.tb_lineno)
        # print('Maybe the key is wrong.')
        # traceback.print_exc()
        return None

if __name__ == '__main__':
    info = tsInfo(r"C:\Users\happy\Desktop\000.ts")
    print(info)