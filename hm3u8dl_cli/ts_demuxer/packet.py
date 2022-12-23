class Packet(object):
    """
    TS包
    """
    def __init__(self, _video_bytes: bytes):
        if not _video_bytes:
            raise Exception('视频数据不能为空！')

        self.sync_byte = _video_bytes[0]
        self.payload_unit_start_indicator = (_video_bytes[1] >> 6) & 1
        self.PID = ((_video_bytes[1] << 8) | _video_bytes[2]) & 0x1fff
        self.afc = (_video_bytes[3] >> 4) & 3
        self.has_payload = self.afc & 1
        self.has_adaptation = self.afc & 2
        if self.has_payload:
            if self.has_adaptation:
                adaptation_field_length = _video_bytes[4]
                self.payload = _video_bytes[5 + adaptation_field_length:]
            else:
                self.payload = _video_bytes[4:]

    def valid(self):
        sync_byte = 0x47
        return self.sync_byte == sync_byte and self.has_payload == 1

    def __str__(self):
        return f'PID:{self.PID}\nhas_payload:{self.has_payload}\n' \
               f'payload_unit_start_indicator:{self.payload_unit_start_indicator}\n' \
               f'payload:{list(self.payload)}\npayload_len:{len(self.payload)}'
