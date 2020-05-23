import mmap

from .patch_charmap import search_charmap
from .cross_references import *
from .extract_strings import extract_strings_from_raw_bytes

import click
from pefile import PE


@click.command()
@click.argument('file_name')
def main(file_name):
    with open(file_name, 'rb') as pe_file:
        file_data = mmap.mmap(pe_file.fileno(), 0, access=mmap.ACCESS_READ)
        pe = PE(data=file_data, fast_load=True)

        code_section = pe.sections[0]
        data_section = pe.sections[1]

        image_base = pe.OPTIONAL_HEADER.ImageBase

        print("Extracting strings... ")
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

        print("Searching for unicode table...")

        unicode_table_rva = search_charmap(data_section.get_data(), data_section.VirtualAddress)
        if unicode_table_rva is None:
            print("Not found.")
        else:
            print("Found at address 0x{:x} (offset 0x{:x})"
                  .format(unicode_table_rva + image_base, pe.get_offset_from_rva(unicode_table_rva)))


if __name__ == '__main__':
    main()
