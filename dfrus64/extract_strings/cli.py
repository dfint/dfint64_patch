import operator
import sys
from typing import BinaryIO, Iterator, Tuple, cast

import click
from loguru import logger
from peclasses.portable_executable import PortableExecutable

from dfrus64.binio import read_section_data
from dfrus64.cross_references.cross_references_relative import (
    find_relative_cross_references,
)
from dfrus64.extract_strings.from_raw_bytes import extract_strings_from_raw_bytes


def extract_strings(pe_file: BinaryIO) -> Iterator[Tuple[int, str]]:
    pe = PortableExecutable(pe_file)

    sections = pe.section_table
    code_section = sections[0]
    string_section = sections[1]

    image_base = cast(int, pe.optional_header.image_base)

    strings = list(
        extract_strings_from_raw_bytes(
            read_section_data(pe_file, string_section),
            base_address=cast(int, string_section.virtual_address) + image_base,
        )
    )

    cross_references = find_relative_cross_references(
        read_section_data(pe_file, code_section),
        base_address=cast(int, code_section.virtual_address) + image_base,
        addresses=map(operator.itemgetter(0), strings),
    )

    for address, string in sorted(strings, key=operator.itemgetter(0)):
        # Only objects with references from the code
        if address in cross_references:
            yield address, string


@click.command()
@click.argument("file_name")
@click.argument("out_file", default=None, required=False)
def main(file_name, out_file):
    with open(file_name, "rb") as pe_file:
        if out_file is None:
            out_file_object = sys.stdout
        else:
            out_file_object = open(out_file, "w")

        for address, string in extract_strings(pe_file):
            logger.info("0x{:X} {!r}", address, string, file=out_file_object)

        if out_file is None:
            out_file_object.close()


if __name__ == "__main__":
    main()