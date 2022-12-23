class Pes(object):
    def __init__(self, _bytes: bytes):
        header_data_length = _bytes[8]
        self.data_byte = _bytes[9 + header_data_length:]

    def __str__(self):
        return f'data_byte:{list(self.data_byte)}'
