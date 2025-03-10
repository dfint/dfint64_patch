from collections.abc import Iterable
from typing import BinaryIO

from dfint64_patch.type_aliases import Offset


def read_bytes(file_object: BinaryIO, offset: Offset, count: int = 1) -> bytes:
    file_object.seek(offset)
    return file_object.read(count)


def write_dword(file_object: BinaryIO, val: int) -> None:
    file_object.write(val.to_bytes(4, byteorder="little"))


def write_dwords(file_object: BinaryIO, dwords: Iterable[int]) -> None:
    for x in dwords:
        write_dword(file_object, x)


def to_dword(number: int, *, signed: bool = False) -> bytes:
    return number.to_bytes(length=4, byteorder="little", signed=signed)


def write_string(
    file_object: BinaryIO,
    s: str,
    offset: Offset | None = None,
    new_len: int | None = None,
    encoding: str | None = None,
) -> None:
    if offset is not None:
        file_object.seek(offset)

    if new_len is None:
        new_len = len(s) + 1

    bs = s.encode() if encoding is None else s.encode(encoding)

    file_object.write(bs.ljust(new_len, b"\0"))
