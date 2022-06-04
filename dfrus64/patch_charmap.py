import codecs
import functools
import unicodedata
from typing import Tuple, Mapping, Iterable, Dict, Union, BinaryIO, Callable

from .binio import write_dwords, write_dword
from .type_aliases import Offset


def ord_utf16(c: str) -> int:
    return int.from_bytes(c.encode("utf-16")[2:], "little")


def chr_utf16(value: int) -> str:
    return value.to_bytes(2, "little").decode("utf-16")


_additional_codepages: Mapping[str, Mapping[int, Union[int, Iterable[int]]]] = {
    "cp437": dict(),  # Stub entry, so that dfrus.py do not complain that cp437 is not implemented
    "cp1251": {
        0xC0: range(ord_utf16("А"), ord_utf16("Я") + 1),
        0xE0: range(ord_utf16("а"), ord_utf16("я") + 1),
        0xA8: ord_utf16("Ё"),
        0xB8: ord_utf16("ё"),
        0xB2: [ord_utf16("І"), ord_utf16("і")],
        # 0xAF: ord_utf16('Ї'),
        0xBF: ord_utf16("ї"),
        0xAA: ord_utf16("Є"),
        0xBA: ord_utf16("є"),
        0xA5: ord_utf16("Ґ"),
        0xB4: ord_utf16("ґ"),
        # 0xA1: ord_utf16('Ў'),
        0xA2: ord_utf16("ў"),
    },
    # Vietnamese code page
    "viscii": {
        0x02: ord_utf16("Ẳ"),
        0x05: [ord_utf16("Ẵ"), ord_utf16("Ẫ")],
        0x14: ord_utf16("Ỷ"),
        0x19: ord_utf16("Ỹ"),
        0x1E: ord_utf16("Ỵ"),
        0x80: map(ord_utf16, "ẠẮẰẶẤẦẨẬẼẸẾỀỂỄỆỐ"),
        0x90: map(ord_utf16, "ỒỔỖỘỢỚỜỞỊỎỌỈỦŨỤỲ"),
        0xA0: map(ord_utf16, "Õắằặấầẩậẽẹếềểễệố"),
        0xB0: map(ord_utf16, "ồổỗỠƠộờởịỰỨỪỬơớƯ"),
        0xC0: map(ord_utf16, "ÀÁÂÃẢĂẳẵÈÉÊẺÌÍĨỳ"),
        0xD0: map(ord_utf16, "ĐứÒÓÔạỷừửÙÚỹỵÝỡư"),
        0xE0: map(ord_utf16, "àáâãảăữẫèéêẻìíĩỉ"),
        0xF0: map(ord_utf16, "đựòóôõỏọụùúũủýợỮ"),
    },
}


def generate_charmap_table_patch(enc1: str, enc2: str) -> Mapping[int, int]:
    bt = bytes(range(0x80, 0x100))
    return dict(
        (i, ord_utf16(b))
        for i, (a, b) in enumerate(zip(bt.decode(enc1), bt.decode(enc2, errors="replace")), start=0x80)
        if a != b and b.isalpha()
    )


@functools.lru_cache(maxsize=None)
def get_codepages() -> Mapping[str, Mapping[int, Union[int, Iterable[int]]]]:
    codepages: Dict[str, Mapping[int, Union[int, Iterable[int]]]] = dict()

    for i in range(700, 1253):
        try:
            codepages["cp%d" % i] = generate_charmap_table_patch("cp437", "cp%d" % i)
        except LookupError:
            pass

    codepages.update(_additional_codepages)

    return codepages


def patch_unicode_table(file: BinaryIO, offset: Offset, codepage: str):
    patch = get_codepages()[codepage]
    for code, value in patch.items():
        file.seek(offset + code * 4)
        if isinstance(value, int):
            write_dword(file, patch[code])
        else:
            write_dwords(file, patch[code])


class Encoder:
    def __init__(self, codepage_data):
        self.lookup_table = dict()

        for char_code, value in codepage_data.items():
            if isinstance(value, int):
                self.lookup_table[chr_utf16(value)] = char_code
            else:
                for i, char in enumerate(value):
                    self.lookup_table[chr_utf16(char)] = char_code + i

    def encode(self, input_string: str, errors="strict") -> Tuple[bytes, int]:
        array = []
        for char in unicodedata.normalize("NFC", input_string):
            if char in self.lookup_table:
                array.append(self.lookup_table[char])
            else:
                array.append(char.encode("cp437", errors=errors)[0])

        return bytes(array), len(array)


_encoders = {"viscii": Encoder(_additional_codepages["viscii"])}


def get_encoder(encoding: str) -> Callable[[str], Tuple[bytes, int]]:
    try:
        return codecs.getencoder(encoding)
    except LookupError as ex:
        if encoding in get_codepages():
            return _encoders[encoding].encode
        else:
            raise ex
