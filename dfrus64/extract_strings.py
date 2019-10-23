import mmap
import sys
import operator
from typing import Tuple, Iterator

import click
from pefile import PE

from .cross_references import find_relative_cross_references
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

    string_length = 0
    number_of_letters = 0
    for i, c in enumerate(buf):
        if c == 0:
            string_length = i
            break

        if not is_allowed(c) or not possible_to_decode(buf[i:i + 1], encoding):
            break
        elif buf[i:i + 1].isalpha():
            number_of_letters += 1

    return string_length, number_of_letters


def extract_strings_from_raw_bytes(bytes_block: bytes, base_address: Rva = 0, alignment=4, encoding='cp437') \
        -> Iterator[Tuple[Rva, str]]:
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
        buffer_part = bytes(view[i:])
        string_len, letters = check_string(buffer_part, encoding)
        if string_len and letters:
            string = bytes(view[i: i + string_len]).decode(encoding)
            yield base_address + i, string
            i += (string_len // alignment + 1) * alignment
            continue

        i += alignment


@click.command()
@click.argument('file_name')
@click.argument('out_file', default=None)
def main(file_name, out_file):
    with open(file_name, 'rb') as pe_file:
        file_data = mmap.mmap(pe_file.fileno(), 0, access=mmap.ACCESS_READ)
        pe = PE(data=file_data, fast_load=True)

        code_section = pe.sections[0]
        string_section = pe.sections[1]

        print(string_section)
        print(hex(string_section.VirtualAddress))

        image_base = pe.OPTIONAL_HEADER.ImageBase

        if out_file is None:
            file = sys.stdout
        else:
            file = open(out_file, 'w')

        strings = list(extract_strings_from_raw_bytes(string_section.get_data(),
                                                      base_address=string_section.VirtualAddress + image_base))

        cross_references = find_relative_cross_references(code_section.get_data(),
                                                          base_address=code_section.VirtualAddress + image_base,
                                                          addresses=map(operator.itemgetter(0), strings))

        for address, string in sorted(strings, key=operator.itemgetter(0)):
            # Only objects with references from the code
            if address in cross_references:
                print(hex(address), string, file=file)

        if out_file is None:
            file.close()


if __name__ == '__main__':
    main()
