import operator
import sys

import click
from loguru import logger
from peclasses.portable_executable import PortableExecutable

from dfrus64.cross_references.cross_references_relative import (
    find_relative_cross_references,
)
from dfrus64.extract_strings.from_raw_bytes import extract_strings_from_raw_bytes


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
                string_section.get_data(),
                base_address=string_section.VirtualAddress + image_base,
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
                logger.info(hex(address), string, file=file)

        if out_file is None:
            file.close()


if __name__ == "__main__":
    main()
