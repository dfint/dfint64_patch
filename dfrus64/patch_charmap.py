from typing import Callable, Tuple

from .binio import write_dwords, to_dword
from .type_aliases import Offset


def ord_utf16(c: str):
    return int.from_bytes(c.encode('utf-16')[2:], 'little')


def chr_utf16(value: int):
    return value.to_bytes(2, 'little').decode('utf-16')


_additional_codepages = {
    'cp437': dict(),  # Stub entry, so that dfrus.py do not complain that cp437 is not implemented
    'cp1251': {
        0xC0: range(ord_utf16('А'), ord_utf16('Я') + 1),
        0xE0: range(ord_utf16('а'), ord_utf16('я') + 1),
        0xA8: [ord_utf16('Ё')],
        0xB8: [ord_utf16('ё')],
        0xB2: [ord_utf16('І'), ord_utf16('і')],
        # 0xAF: ord_utf16('Ї'),
        0xBF: [ord_utf16('ї')],
        0xAA: [ord_utf16('Є')],
        0xBA: [ord_utf16('є')],
        0xA5: [ord_utf16('Ґ')],
        0xB4: [ord_utf16('ґ')],
        # 0xA1: [ord_utf16('Ў')],
        0xA2: [ord_utf16('ў')],
    },
    # Vietnamese code page
    'viscii': {
        0x02: [ord_utf16('Ẳ')],
        0x05: [ord_utf16('Ẵ'), ord_utf16('Ẫ')],
        0x14: [ord_utf16('Ỷ')],
        0x19: [ord_utf16('Ỹ')],
        0x1E: [ord_utf16('Ỵ')],
        0x80: map(ord_utf16, 'ẠẮẰẶẤẦẨẬẼẸẾỀỂỄỆỐ'),
        0x90: map(ord_utf16, 'ỒỔỖỘỢỚỜỞỊỎỌỈỦŨỤỲ'),
        0xA0: map(ord_utf16, 'Õắằặấầẩậẽẹếềểễệố'),
        0xB0: map(ord_utf16, 'ồổỗỠƠộờởịỰỨỪỬơớƯ'),
        0xC0: map(ord_utf16, 'ÀÁÂÃẢĂẳẵÈÉÊẺÌÍĨỳ'),
        0xD0: map(ord_utf16, 'ĐứÒÓÔạỷừửÙÚỹỵÝỡư'),
        0xE0: map(ord_utf16, 'àáâãảăữẫèéêẻìíĩỉ'),
        0xF0: map(ord_utf16, 'đựòóôõỏọụùúũủýợỮ')
    }
}
_codepages = dict()


def generate_charmap_table_patch(enc1, enc2):
    bt = bytes(range(0x80, 0x100))
    return dict((i, ord_utf16(b))
                for i, (a, b) in enumerate(zip(bt.decode(enc1), bt.decode(enc2, errors='replace')), start=0x80)
                if a != b and b.isalpha())


def get_codepages():
    global _codepages
    if not _codepages:
        _codepages = dict()
        for i in range(700, 1253):
            try:
                _codepages['cp%d' % i] = generate_charmap_table_patch('cp437', 'cp%d' % i)
            except LookupError:
                pass
        
        _codepages.update(_additional_codepages)

    return _codepages


def patch_unicode_table(fn, off, codepage):
    cp = get_codepages()[codepage]
    for item in cp:
        write_dwords(fn, off + item*4, cp[item])


def search_charmap(bytes_block: bytes, offset: Offset = 0):
    unicode_table_start = b''.join(
        to_dword(item) for item in [0x20, 0x263A, 0x263B, 0x2665, 0x2666, 0x2663, 0x2660, 0x2022]
    )

    view = memoryview(bytes_block)

    for i in range(len(view)):
        if view[i:i+len(unicode_table_start)] == unicode_table_start:
            return offset + i

    return None


class Encoder:
    def __init__(self, codepage_data):
        self.lookup_table = dict()

        for char_code, value in codepage_data.items():
            if isinstance(value, int):
                self.lookup_table[chr_utf16(value)] = char_code
            else:
                for i, char in enumerate(value):
                    self.lookup_table[chr_utf16(char)] = char_code + i

    def encode(self, input_string: str, errors='strict') -> Tuple[bytes, int]:
        array = []

        for char in input_string:
            if char in self.lookup_table:
                array.append(self.lookup_table[char])
            else:
                array.append(char.encode('cp437', errors=errors)[0])

        return bytes(array), len(array)


_encoders = {'viscii': Encoder(_additional_codepages['viscii'])}


def get_encoder(encoding: str) -> Callable[[str, str], bytes]:
    return lambda text, errors: _encoders[encoding].encode(text, errors=errors)
