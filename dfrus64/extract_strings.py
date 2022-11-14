import operator
import sys
from typing import Iterator, Tuple, Union

import click
from peclasses.portable_executable import PortableExecutable

from .cross_references import find_relative_cross_references
from .type_aliases import *

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


@click.command()
@click.argument("file_name")
@click.argument("out_file", default=None)
def main(file_name, out_file):
    with open(file_name, "rb") as pe_file:
        pe = PortableExecutable(pe_file)

        sections = pe.section_table
        code_section = sections[0]
        string_section = sections[1]

        image_base = pe.optional_header.image_base

        if out_file is None:
            file = sys.stdout
        else:
            file = open(out_file, "w")

        strings = list(
            extract_strings_from_raw_bytes(
                string_section.get_data(), base_address=string_section.VirtualAddress + image_base
            )
        )

        cross_references = find_relative_cross_references(
            code_section.get_data(),
            base_address=code_section.VirtualAddress + image_base,
            addresses=map(operator.itemgetter(0), strings),
        )

        for address, string in sorted(strings, key=operator.itemgetter(0)):
            # Only objects with references from the code
            if address in cross_references:
                print(hex(address), string, file=file)

        if out_file is None:
            file.close()


if __name__ == "__main__":
    main()
