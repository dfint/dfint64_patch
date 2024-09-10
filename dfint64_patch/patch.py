from collections.abc import Iterable, Mapping
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
from dfint64_patch.type_aliases import Rva


def run(patched_file: str | Path, translation_table: list[tuple[str, str]], encoding: str) -> None:
    with Path(patched_file).open("r+b") as pe_file:
        pe = PortableExecutable(pe_file)

        sections = pe.section_table
        code_section = sections[0]
        data_section = sections[1]

        cast(int, pe.optional_header.image_base)

        logger.info("Extracting strings...")
        strings = {
            item.address: item.string
            for item in extract_strings_from_raw_bytes(
                read_section_data(pe_file, data_section),
                base_address=Rva(cast(int, data_section.virtual_address)),
            )
        }

        logger.info(f"Found {len(strings)} string-like objects")

        logger.info("Searching for cross references...")
        cross_references = find_relative_cross_references(
            read_section_data(pe_file, code_section),
            base_address=Rva(cast(int, code_section.virtual_address)),
            addresses=strings,
        )

        object_rva_by_reference = invert_cross_reference_table(cross_references)

        logger.info(f"Found {len(cross_references)} objects with references from code section")
        logger.info(f"In total {sum(map(len, cross_references.values()))} cross references")

        logger.info("Searching intersections in the cross references...")

        intersections = list(find_intersected_cross_references(cross_references))
        print_intersections(intersections, object_rva_by_reference, strings)

        translation_dictionary = dict(translation_table)
        for rva, string in strings.items():
            translation = translation_dictionary.get(string)
            if translation:
                if len(translation) <= len(string):
                    encoded_translation = translation.encode(encoding).ljust(len(string) + 1, b"\x00")
                    pe_file.seek(data_section.rva_to_offset(rva))
                    pe_file.write(encoded_translation)
                else:
                    # TODO: implement this case
                    logger.warning(f"Translation for string {string!r} is longer than original one ({translation!r})")


def print_intersections(
    intersections: Iterable[tuple[Rva, Rva]],
    object_rva_by_reference: Mapping[Rva, Rva],
    strings: dict[Rva, str],
) -> None:
    for ref1, ref2 in intersections:
        obj1_rva = object_rva_by_reference[ref1]
        obj2_rva = object_rva_by_reference[ref2]
        logger.info(
            f"0x{ref1:x} (to 0x{obj1_rva:x} {strings[obj1_rva]!r}) / "
            f"0x{ref2:x} (to 0x{obj2_rva:x} {strings[obj2_rva]!r})",
        )


@click.command()
@click.argument(
    "source_file",
    default="Dwarf Fortress.exe",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.argument("patched_file", default="Dwarf Fortress Patched.exe")
@click.option("--dict", "dictionary_file", help="Path to the dictionary csv file")
@click.option("--encoding", "encoding", help="Encoding for the translation", default="cp437")
@click.option("--cleanup", "cleanup", help="Remove patched file on error", default=False)
def main(source_file: str, patched_file: str, dictionary_file: str, encoding: str, cleanup: bool) -> None:  # noqa: FBT001
    with copy_source_file_context(source_file, patched_file, cleanup=cleanup):
        logger.info("Loading translation file...")

        with Path(dictionary_file).open(encoding="utf-8") as trans:
            translation_table = list(load_translation_file(trans))

        print(source_file)  # TODO: split translation table for debugging

        run(patched_file, translation_table, encoding)


if __name__ == "__main__":
    main()
