import subprocess, os
from hm3u8dl_cli.util import Util


class Merge:  # 合并视频

    def __init__(self, temp_dir: str = None, merge_mode: int = 1):
        self.temp_dir = temp_dir
        self.merge_mode = merge_mode
        self.file_list = []

        for root, dirs, files in os.walk(temp_dir):
            for f in files:
                file = os.path.join(root, f)
                if os.path.isfile(file) and file.endswith('ts'):
                    self.file_list.append(file)
        self.toolsPath = Util.toolsPath()
        if merge_mode == 1:
            self.mode1()
        elif merge_mode == 2:
            self.mode2()
        elif merge_mode == 3:
            try:
                self.mode3()
            except:
                self.mode1()
        else:
            self.mode1()

    def mode1(self):  # 二进制合并
        with open(self.temp_dir + '.mp4', 'ab') as f1:
            for i in self.file_list:
                with open(i, 'rb') as f2:
                    f1.write(f2.read())
                    f2.close()
            f1.close()

    def mode2(self):  # 二进制合并，ffmpeg转码
        self.mode1()
        cmd = f'{self.toolsPath["ffmpeg"]} -i "{self.temp_dir + ".mp4"}" -c copy "{self.temp_dir + "_ffmpeg.mp4"}" -loglevel panic'
        subprocess.call(cmd,shell=True)
        if os.path.exists(self.temp_dir + "_ffmpeg.mp4"):
            Util.delFile(f'{self.temp_dir + ".mp4"}')

    def mode3(self):  # ffmpeg 合并
        # cmd = f'{self.toolsPath["ffmpeg"]} -loglevel panic'
        # a = subprocess.call(cmd, shell=True)

        if not os.path.exists(self.temp_dir + ".mp4"):
            filelist = [f"file './video/{str(i).zfill(6)}.ts'" for i in range(len(self.file_list))]
            with open(self.temp_dir + '/filelist.txt', 'w') as f:
                for i in filelist:
                    f.write(i)
                    f.write('\n')
                f.close()
            cmd = f'{self.toolsPath["ffmpeg"]} -f concat -safe 0 -i "{self.temp_dir + "/filelist.txt"}" -c copy "{self.temp_dir + ".mp4"}" -loglevel panic'
            subprocess.call(cmd,shell=True)

            if not os.path.exists(self.temp_dir + ".mp4"):
                print('FFmpeg path error, merge with binary.')
                self.mode1()


def merge_video_audio(video_filePath, audio_filePath,output_filePath,enableDel = True):
    if os.path.isfile(video_filePath) and os.path.isfile(audio_filePath) and os.path.isfile(output_filePath):
        cmd = f'{Util.toolsPath()["ffmpeg"]} -i "{video_filePath}" -i "{audio_filePath}" -vcodec copy -acodec copy "{output_filePath}" -loglevel panic'
        subprocess.call(cmd,shell=True)
        if enableDel:
            Util.delFile(video_filePath)
            Util.delFile(audio_filePath)
        if os.path.exists(output_filePath):
            return True

