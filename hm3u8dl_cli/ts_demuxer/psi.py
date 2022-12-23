from .packet import Packet
from .pat_section import PATSection
from .pmt_section import PMTSection


class PSI(object):
    __PAT_PID = 0x0000
    __CAT_PID = 0x0001
    __TSDT_PID = 0x0002
    __SDT_PID = 0x0011

    def __init__(self):
        self.pat_table = []
        self.pes_streams = []
        self.currentProgramPID = -1

    def __getattribute__(self, attr):
        if attr == 'currentProgramPID':
            _pmtIds = []
            for i in range(len(self.pat_table)):
                _pmtIds.append(self.pat_table[i].pid)
            return _pmtIds[0] if len(_pmtIds) > 0 else -1

        return super().__getattribute__(attr)

    def parse(self, packet: Packet):
        if self.__PAT_PID == packet.PID:
            self.__parse_pat(packet)
        elif packet.PID == self.currentProgramPID:
            # pass
            self.__parse_pmt(packet)

    def __parse_pat(self, packet: Packet):
        if packet.payload_unit_start_indicator:
            pointer = packet.payload[0]
            data = packet.payload[pointer + 1:]
        else:
            data = packet.payload
        pat = PATSection(data)

        for i in range(len(pat.pmtTable)):
            self.__add_pid_to_pmt(pat.pmtTable[i].programNum, pat.pmtTable[i].program_map_PID)
        return pat

    def __parse_pmt(self, packet: Packet):
        if packet.payload_unit_start_indicator:
            pointer = packet.payload[0]
            data = packet.payload[pointer + 1:]
        else:
            data = packet.payload
        pmt = PMTSection(data)
        for i in range(len(pmt.pes_table)):
            self.__add_pes_stream(pmt.pes_table[i])
        return pmt

    def __add_pes_stream(self, pes_stream):
        def get_program(_id):
            for i in range(len(self.pes_streams)):
                if self.pes_streams[i].id == id:
                    return True
            return False

        flag = get_program(pes_stream.PID)
        if not flag:
            self.pes_streams.append(PesStreams(pes_stream.PID, pes_stream.streamType))

    def __add_pid_to_pmt(self, program_id, pid):

        def get_pmt(_id):
            for i in range(len(self.pat_table)):
                if self.pat_table[i].id == id:
                    return True
            return False

        flag = get_pmt(program_id)

        if not flag:
            self.pat_table.append(PatTable(program_id, pid))

    def find_track(self, pid):

        for i in range(len(self.pes_streams)):
            if self.pes_streams[i].id == pid:
                return self.pes_streams[i]


class PatTable(object):
    def __init__(self, _id, pid):
        self.id = _id
        self.pid = pid

    def __str__(self):
        return f'id:{self.id},pid:{self.pid}'


class PesStreams(object):
    def __init__(self, _id, stream_type):
        self.id = _id
        self.stream_type = stream_type
