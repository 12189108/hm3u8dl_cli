class PATSection(object):
    def __init__(self, payload: bytes):
        section_length = ((payload[1] & 0x0f) << 8) | payload[2]
        _len = section_length - 4 - 5
        self.pmtTable = []
        for n in range(0, _len, 4):
            program_num = (payload[n + 8] << 8) | payload[n + 9]
            if program_num == 0x00:
                pass
            else:
                self.pmtTable.append(PtmTable(program_num, ((payload[10 + n] & 0x1f) << 8) | payload[11 + n]))


class PtmTable(object):
    def __init__(self, program_num, program_map_pid):
        self.programNum = program_num
        self.program_map_PID = program_map_pid
