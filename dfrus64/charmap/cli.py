from typing import cast

import click
from loguru import logger
from peclasses.portable_executable import PortableExecutable

from dfrus64.backup import copy_source_file_context
from dfrus64.charmap.patch_charmap import patch_unicode_table
from dfrus64.charmap.search_charmap import search_charmap


def fix_unicode_table(pe_file, pe: PortableExecutable, data_section, image_base: int, codepage: str):
    if not codepage:
        logger.info("Codepage is not set, skipping unicode table patch")
    else:
        logger.info("Searching for unicode table...")
        unicode_table_rva = search_charmap(data_section.get_data(), data_section.VirtualAddress)

        if unicode_table_rva is None:
            logger.info("Warning: unicode table not found. Skipping.")
        else:
            unicode_table_offset = pe.section_table.rva_to_offset(unicode_table_rva)

            logger.info(
                "Found at address 0x{:x} (offset 0x{:x})".format(
                    unicode_table_rva + image_base,
                    unicode_table_offset,
                )
            )

            try:
                pass
                logger.info(f"Patching unicode table to {codepage}...")
                patch_unicode_table(pe_file, unicode_table_offset, codepage)
            except KeyError:
                logger.info(f"Warning: codepage {codepage} not implemented. Skipping.")
            else:
                logger.info("Done.")


def patch_charmap(patched_file: str, codepage: str):
    with open(patched_file, "r+b") as pe_file:
        pe = PortableExecutable(pe_file)
        sections = pe.section_table
        data_section = sections[1]
        image_base = cast(int, pe.optional_header.image_base)
        fix_unicode_table(pe_file, pe, data_section, image_base, codepage)


@click.command()
@click.argument(
    "source_file",
    default="Dwarf Fortress.exe",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.argument("patched_file", default="Dwarf Fortress Patched.exe")
@click.argument("codepage")
@click.option("--cleanup", "cleanup", help="Remove patched file on error", default=False)
def main(source_file: str, patched_file: str, codepage: str, cleanup: bool) -> None:
    with copy_source_file_context(source_file, patched_file, cleanup):
        patch_charmap(patched_file, codepage)
