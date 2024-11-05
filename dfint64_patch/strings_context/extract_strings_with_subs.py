"""
Extract strings grouped by subroutines
"""

from collections import defaultdict
from dataclasses import dataclass
from operator import itemgetter
from pathlib import Path
from typing import BinaryIO, NamedTuple

from omegaconf import DictConfig
from peclasses.portable_executable import PortableExecutable

from dfint64_patch.binio import read_section_data
from dfint64_patch.config import with_config
from dfint64_patch.cross_references.cross_references_relative import find_relative_cross_references
from dfint64_patch.extract_strings.from_raw_bytes import ExtractedStringInfo, extract_strings_from_raw_bytes
from dfint64_patch.extract_subroutines.from_raw_bytes import SubroutineInfo, extract_subroutines, which_subroutine
from dfint64_patch.type_aliases import Rva


def extract_strings_with_xrefs(pe_file: BinaryIO, pe: PortableExecutable) -> dict[ExtractedStringInfo, list[Rva]]:
    sections = pe.section_table
    code_section = sections[0]
    string_section = sections[1]

    strings = list(
        extract_strings_from_raw_bytes(
            read_section_data(pe_file, string_section),
            base_address=string_section.virtual_address,
        ),
    )

    cross_references = find_relative_cross_references(
        read_section_data(pe_file, code_section),
        base_address=code_section.virtual_address,
        addresses=map(itemgetter(0), strings),
    )

    return {
        string_info: cross_references[string_info.address]
        for string_info in strings
        if cross_references[string_info.address]
    }


class StringCrossReference(NamedTuple):
    string: str
    cross_reference: Rva


def extract_strings_grouped_by_subs(pe_file: BinaryIO) -> dict[Rva, list[StringCrossReference]]:
    pe = PortableExecutable(pe_file)
    sections = pe.section_table
    code_section = sections[0]

    image_base = pe.optional_header.image_base

    strings_with_xrefs = extract_strings_with_xrefs(pe_file, pe)

    subroutines = list(
        extract_subroutines(
            read_section_data(pe_file, code_section),
            base_offset=code_section.virtual_address,
        )
    )

    raw_result: dict[SubroutineInfo, list[StringCrossReference]] = defaultdict(list)
    for string_info, xrefs in strings_with_xrefs.items():
        for xref in xrefs:
            subroutine = which_subroutine(subroutines, xref)
            if not subroutine:
                continue
            raw_result[subroutine].append(StringCrossReference(string_info.string, xref))

    result: dict[Rva, list[StringCrossReference]] = {}
    for subroutine, string_xrefs in sorted(raw_result.items(), key=itemgetter(0)):
        sorted_xrefs = sorted(string_xrefs, key=lambda x: x.cross_reference)
        result[Rva(image_base + subroutine.start)] = sorted_xrefs

    return result


@dataclass
class ExtractConfig(DictConfig):
    file_name: str
    out_file: str | None = None


@with_config(ExtractConfig, ".extract.yaml")
def main(conf: ExtractConfig) -> None:
    with Path(conf.file_name).open("rb") as pe_file:
        for subroutine, strings in extract_strings_grouped_by_subs(pe_file).items():
            print(f"sub_{subroutine:x}:")
            for string in strings:
                print(f"\t{string.string}")

            print()


if __name__ == "__main__":
    main()
