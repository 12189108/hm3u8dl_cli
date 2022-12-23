# -*- coding:utf-8 -*-
from .packet import Packet
from .psi import PSI
from .pes_stream import PesStream


class TsDemux(object):
    """
    TS解复用
    """

    def __init__(self):
        self.__PSI = PSI()
        self.__PES = PesStream(self.__PSI)
        self.__CHUNK_LENGTH = 188

    def start_demux(self, video_data: bytes):
        """
        开始解复用
        :param video_data: ts流数据
        :return: video_bytes 和 audio_bytes
        """
        while len(video_data) >= self.__CHUNK_LENGTH:
            chunk = video_data[0:self.__CHUNK_LENGTH]
            packet = Packet(chunk)
            if packet.valid():
                self.__PSI.parse(packet)
                self.__PES.push_data(packet)
            video_data = video_data[188:]

        if len(video_data) < 1:
            self.__PES.assemble_one_pes()

        return TsData(self.__PES.video_bytes, self.__PES.audio_bytes)


class TsData(object):
    """
    TS音视频数据
    """

    def __init__(self, video_bytes, audio_bytes):
        self.video_bytes = video_bytes
        self.audio_bytes = audio_bytes
