class PMTSection(object):
    def __init__(self, payload: bytes):
        self.payload = payload
        self._get_stream_type()

    def _get_stream_type(self, ):
        section_length = ((self.payload[1] & 0x0f) << 8) | self.payload[2]
        program_info_length = ((self.payload[10] & 0x0f) << 8) | self.payload[11]
        if program_info_length < 0:
            return
        es_section_pos = 12 + program_info_length
        es_section_len = section_length - program_info_length - 9 - 4
        es_section_end = es_section_pos + es_section_len
        if es_section_pos >= es_section_end:
            print(f'es_section_pos < es_section_end {es_section_pos},{es_section_end}')
            return
        self.pes_table = []
        i = 0
        while i < es_section_len:
            base_pos = es_section_pos + i
            stream_type = self.payload[base_pos]
            elementary_pid = ((self.payload[base_pos + 1] << 8) | self.payload[base_pos + 2]) & 0x1fff
            es_info_length = ((self.payload[base_pos + 3] << 8) | self.payload[base_pos + 4]) & 0x0fff
            self.pes_table.append(PesTable(stream_type, elementary_pid))
            i += es_info_length + 5


class PesTable(object):
    def __init__(self, stream_type, pid):
        self.streamType = stream_type
        self.PID = pid
