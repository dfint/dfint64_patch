from dfrus64.binio import to_dword
from dfrus64.type_aliases import Offset


def search_charmap(bytes_block: bytes, offset: Offset = 0):
    unicode_table_start = b''.join(
        to_dword(item) for item in [0x20, 0x263A, 0x263B, 0x2665, 0x2666, 0x2663, 0x2660, 0x2022]
    )

    view = memoryview(bytes_block)

    for i in range(len(view)):
        if view[i:i+len(unicode_table_start)] == unicode_table_start:
            return offset + i

    return None
