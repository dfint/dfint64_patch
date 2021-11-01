import os
from typing import Optional

import click
import mmap
from pefile import PE
from shutil import copy
from contextlib import contextmanager

from .patch_charmap import patch_unicode_table
from .search_charmap import search_charmap
from .cross_references import *
from .extract_strings import extract_strings_from_raw_bytes


def fix_unicode_table(pe_file, pe: PE, data_section, image_base: int, codepage: str):
    if not codepage:
        print("Codepage is not set, skipping unicode table patch")
    else:
        print("Searching for unicode table...")
        unicode_table_rva = search_charmap(data_section.get_data(), data_section.VirtualAddress)
        unicode_table_offset = pe.get_offset_from_rva(unicode_table_rva)

        if unicode_table_rva is None:
            print("Warning: unicode table not found. Skipping.")
        else:
            print("Found at address 0x{:x} (offset 0x{:x})"
                  .format(unicode_table_rva + image_base, unicode_table_offset))

            try:
                pass
                print(f"Patching unicode table to {codepage}...")
                patch_unicode_table(pe_file, unicode_table_offset, codepage)
            except KeyError:
                print(f"Warning: codepage {codepage} not implemented. Skipping.")
            else:
                print("Done.")


def run(source_file: str, patched_file: str, translation_table: Mapping[str, str], codepage: str):
    with open(patched_file, 'r+b') as pe_file:
        file_data = mmap.mmap(pe_file.fileno(), 0, access=mmap.ACCESS_READ + mmap.ACCESS_WRITE)
        pe = PE(data=file_data, fast_load=True)

        code_section = pe.sections[0]
        data_section = pe.sections[1]

        image_base = pe.OPTIONAL_HEADER.ImageBase

        print("Extracting strings...")
        strings = dict(extract_strings_from_raw_bytes(data_section.get_data(),
                                                      base_address=data_section.VirtualAddress + image_base))

        print('Found', len(strings), 'string-like objects')

        print('Searching for cross references...')
        cross_references = find_relative_cross_references(code_section.get_data(),
                                                          base_address=code_section.VirtualAddress + image_base,
                                                          addresses=strings)

        object_rva_by_reference = invert_cross_reference_table(cross_references)

        print('Found', len(cross_references), 'objects with references from code section')
        print('In total', sum(map(len, cross_references.values())), 'cross references')

        print("Searching intersections in the cross references...")

        intersections = find_intersected_cross_references(cross_references)

        for ref1, ref2 in intersections:
            obj1_rva = object_rva_by_reference[ref1]
            obj2_rva = object_rva_by_reference[ref2]
            print('0x{:x} (to 0x{:x} {!r}) / '
                  '0x{:x} (to 0x{:x} {!r})'
                  .format(ref1, obj1_rva, strings[obj1_rva],
                          ref2, obj2_rva, strings[obj2_rva]))

        fix_unicode_table(pe_file, pe, data_section, image_base, codepage)

        for string_rva, string in strings.items():
            translation = translation_table.get(string)
            if translation:
                pass


@contextmanager
def destination_file_context(src, dest, cleanup):
    print("Copying '{}'\nTo '{}'...".format(src, dest))
    try:
        copy(src, dest)
    except IOError as ex:
        print("Failed.")
        raise ex
    else:
        print("Success.")

    try:
        yield dest
    except Exception as ex:
        if cleanup:
            print("Removing '{}'".format(dest))
            os.remove(dest)
        raise ex


@click.command()
@click.argument('source_file', default='Dwarf Fortress.exe',
                type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('patched_file', default='Dwarf Fortress Patched.exe')
@click.option('--dict', 'dictionary_file', help='Path to the dictionary csv file')
@click.option('--codepage', 'codepage', help='Enable support of the given codepage by name', default=None)
@click.option('--cleanup', 'cleanup', help='Remove patched file on error', default=False)
def main(source_file: str,
         patched_file: str,
         codepage: Optional[str],
         dictionary_file: str,
         cleanup: bool) -> None:
    
    with destination_file_context(source_file, patched_file, cleanup):
        # TODO: load translation table
        translation_table = dict()  # stub

        # TODO: split translation table for debugging

        run(source_file, patched_file, translation_table, codepage)


if __name__ == '__main__':
    main()
