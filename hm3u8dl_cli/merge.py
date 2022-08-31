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
        self.toolsPath = Util().toolsPath()
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
        # python 3.10
        # match merge_mode:
        #     case 1:
        #         self.mode1()
        #     case 2:
        #         self.mode2()
        #     case 3:
        #         self.mode3()
        #     case _:
        #         self.mode1()



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
            Util().delFile(f'{self.temp_dir + ".mp4"}')

    def mode3(self):  # ffmpeg 合并
        if not os.path.exists(self.temp_dir + ".mp4"):
            cmd = f'{self.toolsPath["ffmpeg"]} -loglevel panic'
            subprocess.call(cmd,shell=True)
            filelist = [f"file './video/{str(i).zfill(6)}.ts'" for i in range(len(self.file_list))]
            with open(self.temp_dir + '/filelist.txt', 'w') as f:
                for i in filelist:
                    f.write(i)
                    f.write('\n')
                f.close()
            cmd = f'{self.toolsPath["ffmpeg"]} -f concat -safe 0 -i "{self.temp_dir + "/filelist.txt"}" -c copy "{self.temp_dir + ".mp4"}" -loglevel panic'
            subprocess.call(cmd,shell=True)


def merge_video_audio(video_dir, audio_dir,output_dir):
    cmd = f'{Util().toolsPath()["ffmpeg"]} -i "{video_dir}" -i "{audio_dir}" -vcodec copy -acodec copy "{output_dir}" -loglevel panic'
    subprocess.call(cmd,shell=True)
    if os.path.exists(output_dir):
        Util().delFile(video_dir)
        Util().delFile(audio_dir)
