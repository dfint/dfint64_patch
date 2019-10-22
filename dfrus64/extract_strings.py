from typing import Mapping, List
from collections import defaultdict

from pefile import PE

from .type_aliases import *

forbidden = set(b'$^')
allowed = set(b'\r\t')


def is_allowed(x: int) -> bool:
    return x in allowed or (ord(' ') <= x and x not in forbidden)


def possible_to_decode(c: bytes, encoding) -> bool:
    try:
        c.decode(encoding=encoding)
    except UnicodeDecodeError:
        return False
    else:
        return True


def check_string(buf: bytes, encoding) -> (int, int):
    """
    Try to decode bytes as a string in the given encoding
    :param buf: byte buffer
    :param encoding: string encoding
    :return: (string_length: int, number_of_letters: int)
    """

    s_len = 0
    letters = 0
    for i, c in enumerate(buf):
        if c == 0:
            s_len = i
            break

        if not is_allowed(c) or not possible_to_decode(buf[i:i + 1], encoding):
            break
        elif buf[i:i + 1].isalpha():
            letters += 1

    return s_len, letters


def extract_strings_from_raw_bytes(bytes_block: bytes, base_address: Rva = 0, alignment=4, encoding='cp437') -> Mapping[Rva, str]:
    """
    Extract all objects which are seem to be text strings from a raw bytes block
    :param bytes_block: block of bytes to be analyzed
    :param base_address: base address of the bytes block
    :param alignment: alignment of strings
    :param encoding: string encoding
    :return: Mapping[string_address: Rva, string: str]
    """
    view = memoryview(bytes_block)
    strings = dict()

    i = 0
    while i < len(view):
        buffer_part = bytes(view[i:])
        string_len, letters = check_string(buffer_part, encoding)
        if string_len and letters:
            strings[base_address+i] = bytes(view[i: i+string_len]).decode(encoding)
            i += (string_len // alignment + 1) * alignment
            continue

        i += alignment

    return strings


def find_relative_cross_references(bytes_block: bytes, base_address: Rva, addresses: List[Rva]) -> Mapping[Rva, List[Rva]]:
    """
    Analyse a block of bytes and try to find relative cross references to the given objects' addresses
    :param bytes_block: bytes block to analyze
    :param base_address: base address of the given block
    :param addresses: list of addresses of objects
    :return: Mapping[object_rva: Rva, cross_references: List[Rva]]
    """
    view = memoryview(bytes_block)
    result = defaultdict(list)
    addresses = set(addresses)

    for i in range(len(bytes_block)-3):
        relative_offset = int.from_bytes(bytes(view[i:i+4]), byteorder='little', signed=True)
        if relative_offset < 0:
            continue

        destination = base_address + i + 4 + relative_offset

        if destination in addresses:
            result[destination].append(base_address + i)

    return result
