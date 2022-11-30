from typing import List, Optional, Tuple, cast

import click
from loguru import logger
from peclasses.portable_executable import PortableExecutable
from peclasses.section_table import Section

from binio import read_section_data
from dfrus64.backup import copy_source_file_context
from dfrus64.charmap.cli import patch_charmap
from dfrus64.cross_references.cross_references_relative import (
    find_intersected_cross_references,
    find_relative_cross_references,
    invert_cross_reference_table,
)
from dfrus64.dictionary_loaders.csv_loader import load_translation_file
from dfrus64.extract_strings.from_raw_bytes import extract_strings_from_raw_bytes


def run(source_file: str, patched_file: str, translation_table: List[Tuple[str, str]], codepage: str):
    patch_charmap(patched_file, codepage)

    with open(patched_file, "r+b") as pe_file:
        pe = PortableExecutable(pe_file)

        sections = pe.section_table
        code_section: Section = sections[0]
        data_section: Section = sections[1]

        image_base = cast(int, pe.optional_header.image_base)

        logger.info("Extracting strings...")
        strings = dict(
            extract_strings_from_raw_bytes(
                read_section_data(pe_file, data_section),
                base_address=data_section.VirtualAddress + image_base,
            )
        )

        logger.info("Found", len(strings), "string-like objects")

        logger.info("Searching for cross references...")
        cross_references = find_relative_cross_references(
            read_section_data(pe_file, code_section),
            base_address=code_section.VirtualAddress + image_base,
            addresses=strings,
        )

        object_rva_by_reference = invert_cross_reference_table(cross_references)

        logger.info("Found", len(cross_references), "objects with references from code section")
        logger.info("In total", sum(map(len, cross_references.values())), "cross references")

        logger.info("Searching intersections in the cross references...")

        intersections = find_intersected_cross_references(cross_references)

        for ref1, ref2 in intersections:
            obj1_rva = object_rva_by_reference[ref1]
            obj2_rva = object_rva_by_reference[ref2]
            logger.info(
                "0x{:x} (to 0x{:x} {!r}) / "
                "0x{:x} (to 0x{:x} {!r})".format(ref1, obj1_rva, strings[obj1_rva], ref2, obj2_rva, strings[obj2_rva])
            )

        translation_dictionary = dict(translation_table)
        for string_rva, string in strings.items():
            translation = translation_dictionary.get(string)
            if translation:
                pass


@click.command()
@click.argument(
    "source_file",
    default="Dwarf Fortress.exe",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.argument("patched_file", default="Dwarf Fortress Patched.exe")
@click.option("--dict", "dictionary_file", help="Path to the dictionary csv file")
@click.option("--codepage", "codepage", help="Enable support of the given codepage by name", default=None)
@click.option("--cleanup", "cleanup", help="Remove patched file on error", default=False)
def main(source_file: str, patched_file: str, codepage: Optional[str], dictionary_file: str, cleanup: bool) -> None:

    with copy_source_file_context(source_file, patched_file, cleanup):
        logger.info("Loading translation file...")

        with open(dictionary_file, encoding="utf-8") as trans:
            translation_table = list(load_translation_file(trans))

        # TODO: split translation table for debugging

        run(source_file, patched_file, translation_table, codepage)


if __name__ == "__main__":
    main()
