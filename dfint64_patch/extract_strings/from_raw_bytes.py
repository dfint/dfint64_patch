"""
Portable Executable x64 mostly has relative cross-reference to static objects (strings),
and they don't appear in a relocation table.
So it is only possible to find strings by linear search in the data section, and then find relative cross-references
in the code section.
"""

from collections.abc import Iterator
from typing import NamedTuple

from dfint64_patch.type_aliases import RVA0, Rva

forbidden: str = "$^@"

ASCII_MAX_CHAR = chr(127)


def is_allowed(c: str) -> bool:
    return " " <= c <= ASCII_MAX_CHAR and c not in forbidden


def check_string(buf: str) -> bool:
    """
    Check that the buffer contain letters and doesn't contain forbidden characters

    :param buf: byte buffer
    :return: number_of_letters: int
    """
    return any(c.isalpha() for c in buf) and all(is_allowed(c) for c in buf)


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
    i = 0
    while i < len(bytes_block):
        if bytes_block[i] == b"\0":
            i += alignment
            continue

        end_index = bytes_block.index(b"\0", i)
        string_len = end_index - i
        buffer_part = bytes_block[i:end_index]

        try:
            string = bytes(buffer_part).decode(encoding)
            if check_string(string):
                yield ExtractedStringInfo(Rva(base_address + i), string)
        except UnicodeDecodeError:
            pass

        i += (string_len // alignment + 1) * alignment
