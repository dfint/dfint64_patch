from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import cast

from loguru import logger
from peclasses.portable_executable import PortableExecutable

from dfint64_patch.binio import read_section_data
from dfint64_patch.cross_references.cross_references_relative import (
    find_intersected_cross_references,
    find_relative_cross_references,
    invert_cross_reference_table,
)
from dfint64_patch.extract_strings.from_raw_bytes import extract_strings_from_raw_bytes
from dfint64_patch.type_aliases import Rva


def patch(patched_file: str | Path, translation_table: list[tuple[str, str]], encoding: str) -> None:
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
                    # Shorter strings are padded with spaces
                    encoded_translation = translation.encode(encoding).ljust(len(string) + 1) + b"\0"
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