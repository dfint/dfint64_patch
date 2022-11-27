from typing import BinaryIO, Iterable

from dfrus64.type_aliases import Offset


def read_bytes(file_object: BinaryIO, offset: Offset, count=1) -> bytes:
    file_object.seek(offset)
    return file_object.read(count)


def write_dword(file_object: BinaryIO, val: int):
    file_object.write(val.to_bytes(4, byteorder="little"))


def write_dwords(file_object: BinaryIO, dwords: Iterable[int]):
    for x in dwords:
        write_dword(file_object, x)


def to_dword(number: int, signed: bool = False, byteorder: str = "little"):
    return number.to_bytes(length=4, byteorder=byteorder, signed=signed)


def write_string(file_object: BinaryIO, s: str, offset: Offset = None, new_len: int = None, encoding: str = None):
    if offset is not None:
        file_object.seek(offset)

    if new_len is None:
        new_len = len(s) + 1

    if encoding is None:
        s = s.encode()
    else:
        s = s.encode(encoding)

    file_object.write(s.ljust(new_len, b"\0"))
