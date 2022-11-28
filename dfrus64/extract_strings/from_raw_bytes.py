"""
Portable Executable x64 mostly has relative cross-reference to static objects (strings),
and they don't appear in a relocation table.
So it is only possible to find strings by linear search in the data section, and then find relative cross-references
in the code section.
"""

from typing import Iterator, Tuple, Union

from dfrus64.type_aliases import Rva

forbidden = set(b"$^")
allowed = set(b"\r\t")


def is_allowed(x: int) -> bool:
    return x in allowed or (ord(" ") <= x and x not in forbidden)


def possible_to_decode(c: bytes, encoding) -> bool:
    try:
        c.decode(encoding=encoding)
    except UnicodeDecodeError:
        return False
    else:
        return True


def check_string(buf: Union[bytes, memoryview], encoding: str) -> (int, int):
    """
    Try to decode bytes as a string in the given encoding
    :param buf: byte buffer
    :param encoding: string encoding
    :return: (string_length: int, number_of_letters: int)
    """

    string_length = 0
    number_of_letters = 0
    for i, c in enumerate(buf):
        if c == 0:
            string_length = i
            break

        current_byte = bytes(buf[i : i + 1])
        if not is_allowed(c) or not possible_to_decode(current_byte, encoding):
            break
        elif current_byte.isalpha():
            number_of_letters += 1

    return string_length, number_of_letters


def extract_strings_from_raw_bytes(
    bytes_block: bytes, base_address: Rva = 0, alignment=4, encoding="cp437"
) -> Iterator[Tuple[Rva, str]]:
    """
    Extract all objects which are seem to be text strings from a raw bytes block
    :param bytes_block: block of bytes to be analyzed
    :param base_address: base address of the bytes block
    :param alignment: alignment of strings
    :param encoding: string encoding
    :return: Iterator[Tuple[string_address: Rva, string: str]]
    """
    view = memoryview(bytes_block)

    i = 0
    while i < len(view):
        buffer_part = view[i:]
        string_len, letters = check_string(buffer_part, encoding)
        if string_len and letters:
            string = bytes(view[i : i + string_len]).decode(encoding)
            yield base_address + i, string
            i += (string_len // alignment + 1) * alignment
            continue

        i += alignment
