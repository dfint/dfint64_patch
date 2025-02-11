import operator
from dataclasses import dataclass
from io import BufferedReader
from pathlib import Path

import lief
from omegaconf import DictConfig

from dfint64_patch.config import with_config
from dfint64_patch.cross_references.cross_references_relative import (
    find_relative_cross_references,
)
from dfint64_patch.extract_strings.from_raw_bytes import (
    ExtractedStringInfo,
    extract_strings_from_raw_bytes,
)
from dfint64_patch.type_aliases import Rva
from dfint64_patch.utils import maybe_open


def extract_strings(pe_file: BufferedReader) -> list[ExtractedStringInfo]:
    pe = lief.PE.parse(pe_file)
    assert pe is not None

    code_section = pe.sections[0]
    string_section = pe.sections[1]

    image_base = pe.optional_header.imagebase

    strings = list(
        extract_strings_from_raw_bytes(
            string_section.content,
            base_address=Rva(string_section.virtual_address + image_base),
        ),
    )

    cross_references = find_relative_cross_references(
        code_section.content,
        base_address=Rva(code_section.virtual_address + image_base),
        addresses=map(operator.itemgetter(0), strings),
    )

    filtered = filter(lambda x: x[0] in cross_references, strings)
    return sorted(filtered, key=lambda s: min(cross_references[s.address]))


@dataclass
class ExtractConfig(DictConfig):
    file_name: str
    out_file: str | None = None


@with_config(ExtractConfig, ".extract.yaml")
def main(conf: ExtractConfig) -> None:
    with Path(conf.file_name).open("rb") as pe_file, maybe_open(conf.out_file) as out_file_object:
        for item in extract_strings(pe_file):
            print(item.string, file=out_file_object)


if __name__ == "__main__":
    main()
