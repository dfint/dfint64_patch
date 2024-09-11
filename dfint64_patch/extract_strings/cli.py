import operator
import sys
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, TextIO, cast

from loguru import logger
from omegaconf import DictConfig
from peclasses.portable_executable import PortableExecutable

from dfint64_patch.binio import read_section_data
from dfint64_patch.config import with_config
from dfint64_patch.cross_references.cross_references_relative import (
    find_relative_cross_references,
)
from dfint64_patch.extract_strings.from_raw_bytes import (
    ExtractedStringInfo,
    extract_strings_from_raw_bytes,
)
from dfint64_patch.type_aliases import Rva


def extract_strings(pe_file: BinaryIO) -> Iterator[ExtractedStringInfo]:
    pe = PortableExecutable(pe_file)

    sections = pe.section_table
    code_section = sections[0]
    string_section = sections[1]

    image_base = pe.optional_header.image_base

    strings = list(
        extract_strings_from_raw_bytes(
            read_section_data(pe_file, string_section),
            base_address=Rva(cast(int, string_section.virtual_address) + image_base),
        ),
    )

    cross_references = find_relative_cross_references(
        read_section_data(pe_file, code_section),
        base_address=Rva(cast(int, code_section.virtual_address) + image_base),
        addresses=map(operator.itemgetter(0), strings),
    )

    filtered = filter(lambda x: x[0] in cross_references, strings)
    result = sorted(filtered, key=lambda s: min(cross_references[s.address]))

    yield from result


@contextmanager
def maybe_open(file_name: str | None) -> Generator[TextIO, None, None]:
    """
    Open a file if the name is provided, and close it on exit from with-block,
    or provide stdout as a file object, if the file_name parameter is None
    :param file_name: file name or None
    :return: file object
    """
    file_object = sys.stdout if file_name is None or file_name == "stdout" else Path(file_name).open("w")  # noqa: SIM115

    try:
        yield file_object
    finally:
        if file_object != sys.stdout:
            file_object.close()


@dataclass
class ExtractConfig(DictConfig):
    file_name: str
    out_file: str | None = None


@with_config(ExtractConfig, ".extract.yaml")
def main(conf: ExtractConfig) -> None:
    with Path(conf.file_name).open("rb") as pe_file, maybe_open(conf.out_file) as out_file_object:
        for address, string in extract_strings(pe_file):
            print(string, file=out_file_object)
            logger.info(f"0x{address:X} {string!r}")


if __name__ == "__main__":
    main()
