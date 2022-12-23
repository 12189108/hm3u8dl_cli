from .psi import PSI
from .packet import Packet
from .pes import Pes


class PesStream(object):
    def __init__(self, psi: PSI):
        self.PID = None
        self.psi = psi
        self.cache_bytes = b''
        self.audio_bytes = b''
        self.video_bytes = b''

    def push_data(self, packet: Packet):
        if 0x001f < packet.PID < 0x1fff:
            if self.psi.currentProgramPID == -1:
                self.push_packet(packet)
            elif self.psi.currentProgramPID != packet.PID:
                if packet.payload_unit_start_indicator == 1:
                    self.assemble_one_pes()
                self.push_packet(packet)

    def push_packet(self, packet: Packet):
        empty = len(self.cache_bytes) < 1
        if empty and packet.payload_unit_start_indicator == 0:
            return
        if empty:
            self.PID = packet.PID
        self.cache_bytes += packet.payload

    def assemble_one_pes(self):
        if len(self.cache_bytes) > 0:
            pes_data = Pes(self.cache_bytes)
            track = self.psi.find_track(self.PID)
            self.cache_bytes = b''
            if track:
                data = TsStream(track.id, track.stream_type, pes_data)
                if data.stream_type == 15:
                    self.audio_bytes += data.pes.data_byte
                elif data.stream_type == 27 or data.stream_type == 36:
                    self.video_bytes += data.pes.data_byte


class TsStream(object):
    def __init__(self, pid, stream_type, pes):
        self.pid = pid
        self.stream_type = stream_type
        self.pes = pes

    def __str__(self):
        return f'pid:{self.pid}\n' \
               f'stream_type:{self.stream_type}\n' \
               f'pes_length:{len(self.pes.data_byte)}'
