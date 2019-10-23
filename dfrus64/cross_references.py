from collections import defaultdict
from itertools import chain
from typing import List, Mapping, Tuple, Iterable

from dfrus64.type_aliases import Rva


def find_relative_cross_references(bytes_block: bytes, base_address: Rva, addresses: Iterable[Rva]) \
        -> Mapping[Rva, List[Rva]]:
    """
    Analyse a block of bytes and try to find relative cross references to the given objects' addresses
    :param bytes_block: bytes block to analyze
    :param base_address: base address of the given block
    :param addresses: list of addresses of objects
    :return: Mapping[object_rva: Rva, cross_references: List[Rva]]
    """
    view = memoryview(bytes_block)
    result = defaultdict(list)
    addresses = set(addresses)

    for i in range(len(bytes_block)-3):
        relative_offset = int.from_bytes(bytes(view[i:i+4]), byteorder='little', signed=True)

        destination = base_address + i + 4 + relative_offset

        if destination in addresses:
            result[destination].append(base_address + i)

    return result


def invert_cross_reference_table(cross_references: Mapping[Rva, List[Rva]]) -> Mapping[Rva, Rva]:
    result = dict()
    for object_rva, references in cross_references.items():
        for ref in references:
            result[ref] = object_rva

    return result


def find_intersected_cross_references(cross_references: Mapping[Rva, List[Rva]]) -> Iterable[Tuple[Rva, Rva]]:
    references = sorted(chain.from_iterable(cross_references.values()))

    for i, item in enumerate(references):
        j = i + 1
        while j < len(references) and references[j] - item < 4:
            yield item, references[j]
            j += 1
