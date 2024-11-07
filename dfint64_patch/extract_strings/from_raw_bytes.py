"""
Portable Executable x64 mostly has relative cross-reference to static objects (strings),
and they don't appear in a relocation table.
So it is only possible to find strings by linear search in the data section, and then find relative cross-references
in the code section.
"""

from collections.abc import Iterator
from typing import NamedTuple

from dfint64_patch.type_aliases import RVA0, Rva

forbidden: set[int] = set(b"$^@")
allowed: set[int] = set()

ASCII_MAX_CODE = 127


def is_allowed(x: int) -> bool:
    return x in allowed or (ord(" ") <= x <= ASCII_MAX_CODE and x not in forbidden)


def check_string(buf: bytes | memoryview) -> int | None:
    """
    Check that the buffer contain letters and doesn't contain forbidden characters

    :param buf: byte buffer
    :return: number_of_letters: int
    """

    number_of_letters = 0
    for i, c in enumerate(buf):
        current_byte = bytes(buf[i : i + 1])
        if not is_allowed(c):
            return None

        if current_byte.isalpha():
            number_of_letters += 1

    return number_of_letters


class ExtractedStringInfo(NamedTuple):
    address: Rva
    string: str


def extract_strings_from_raw_bytes(
    bytes_block: bytes,
    base_address: Rva = RVA0,
    alignment: int = 4,
    encoding: str = "cp437",
) -> Iterator[ExtractedStringInfo]:
    """
    Extract all objects which are seem to be text strings from a raw bytes block
    :param bytes_block: a block of bytes to be analyzed
    :param base_address: base address of the bytes block
    :param alignment: alignment of strings
    :param encoding: string encoding
    :return: Iterator[ExtractedStringInfo]
    """
    view = memoryview(bytes_block)

    i = 0
    while i < len(bytes_block):
        if bytes_block[i] == b"\0":
            i += alignment
            continue

        end_index = bytes_block.index(b"\0", i)
        string_len = end_index - i
        buffer_part = view[i:end_index]

        if check_string(buffer_part):
            try:
                string = bytes(buffer_part).decode(encoding)
                yield ExtractedStringInfo(Rva(base_address + i), string)
            except UnicodeDecodeError:
                pass

        i += (string_len // alignment + 1) * alignment
