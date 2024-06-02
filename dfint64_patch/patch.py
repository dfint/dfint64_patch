from pathlib import Path
from typing import cast

import click
from loguru import logger
from peclasses.portable_executable import PortableExecutable

from dfint64_patch.backup import copy_source_file_context
from dfint64_patch.binio import read_section_data
from dfint64_patch.cross_references.cross_references_relative import (
    find_intersected_cross_references,
    find_relative_cross_references,
    invert_cross_reference_table,
)
from dfint64_patch.dictionary_loaders.csv_loader import load_translation_file
from dfint64_patch.extract_strings.from_raw_bytes import extract_strings_from_raw_bytes


def run(source_file: str, patched_file: str, translation_table: list[tuple[str, str]]) -> None:
    with Path(patched_file).open("r+b") as pe_file:
        pe = PortableExecutable(pe_file)

        sections = pe.section_table
        code_section = sections[0]
        data_section = sections[1]

        image_base = cast(int, pe.optional_header.image_base)

        logger.info("Extracting strings...")
        strings = dict(
            extract_strings_from_raw_bytes(
                read_section_data(pe_file, data_section),
                base_address=cast(int, data_section.virtual_address) + image_base,
            ),
        )

        logger.info("Found", len(strings), "string-like objects")

        logger.info("Searching for cross references...")
        cross_references = find_relative_cross_references(
            read_section_data(pe_file, code_section),
            base_address=cast(int, code_section.virtual_address) + image_base,
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
                f"0x{ref1:x} (to 0x{obj1_rva:x} {strings[obj1_rva]!r}) / "
                f"0x{ref2:x} (to 0x{obj2_rva:x} {strings[obj2_rva]!r})",
            )

        translation_dictionary = dict(translation_table)
        for string in strings.values():
            translation = translation_dictionary.get(string)
            if translation:
                ...  # work in progress...

        print(source_file)


@click.command()
@click.argument(
    "source_file",
    default="Dwarf Fortress.exe",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.argument("patched_file", default="Dwarf Fortress Patched.exe")
@click.option("--dict", "dictionary_file", help="Path to the dictionary csv file")
@click.option("--cleanup", "cleanup", help="Remove patched file on error", default=False)
def main(source_file: str, patched_file: str, dictionary_file: str, cleanup: bool) -> None:  # noqa: FBT001
    with copy_source_file_context(source_file, patched_file, cleanup):
        logger.info("Loading translation file...")

        with Path(dictionary_file).open(encoding="utf-8") as trans:
            translation_table = list(load_translation_file(trans))

        print(source_file)  # TODO: split translation table for debugging

        run(source_file, patched_file, translation_table)


if __name__ == "__main__":
    main()
