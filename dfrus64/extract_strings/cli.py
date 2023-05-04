import operator
import sys
from contextlib import contextmanager
from typing import BinaryIO, Iterator, Optional, cast

import click
from loguru import logger
from peclasses.portable_executable import PortableExecutable

from dfrus64.binio import read_section_data
from dfrus64.cross_references.cross_references_relative import (
    find_relative_cross_references,
)
from dfrus64.extract_strings.from_raw_bytes import (
    ExtractedStringInfo,
    extract_strings_from_raw_bytes,
)


def extract_strings(pe_file: BinaryIO) -> Iterator[ExtractedStringInfo]:
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

    filtered = filter(lambda x: x[0] in cross_references, strings)
    result = sorted(filtered, key=lambda s: min(cross_references[s.offset]))

    yield from result


@contextmanager
def maybe_open(file_name: Optional[str]):
    """
    Open a file if the name is provided, and close it on exit from with-block,
    or provide stdout as a file object, if the file_name parameter is None
    :param file_name: file name or None
    :return:
    """
    if file_name is None:
        file_object = sys.stdout
    else:
        file_object = open(file_name, "w")

    try:
        yield file_object
    finally:
        if file_object != sys.stdout:
            file_object.close()


@click.command()
@click.argument("file_name")
@click.argument("out_file", default=None, required=False)
def main(file_name, out_file):
    with open(file_name, "rb") as pe_file, maybe_open(out_file) as out_file_object:
        for address, string in extract_strings(pe_file):
            print(string, file=out_file_object)
            logger.info("0x{:X} {!r}", address, string, file=out_file_object)


if __name__ == "__main__":
    main()
