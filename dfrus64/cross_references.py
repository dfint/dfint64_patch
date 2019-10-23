from collections import defaultdict
from typing import List, Mapping

from dfrus64.type_aliases import Rva


def find_relative_cross_references(bytes_block: bytes, base_address: Rva, addresses: List[Rva]) -> Mapping[Rva, List[Rva]]:
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
