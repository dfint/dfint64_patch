from collections import defaultdict
from itertools import chain
from typing import Iterable, Iterator, List, Mapping, Tuple

from dfint64_patch.type_aliases import Rva


def find_relative_cross_references(
    bytes_block: bytes, base_address: Rva, addresses: Iterable[Rva]
) -> Mapping[Rva, List[Rva]]:
    """
    Analyse a block of bytes and try to find relative cross-references to the given objects' addresses
    :param bytes_block: bytes block to analyse
    :param base_address: base address of the given block
    :param addresses: an iterable of addresses. In addition to list and other flat types it also can be range
        (e.g. `range(0x11000, 0x12000)`) or dict object.
    :return: Mapping[object_rva: Rva, cross_references: List[Rva]]
    """
    view = memoryview(bytes_block)
    result = defaultdict(list)

    if not isinstance(addresses, (range, dict)):
        addresses = set(addresses)

    for i in range(len(bytes_block) - 3):
        relative_offset = int.from_bytes(bytes(view[i : i + 4]), byteorder="little", signed=True)

        destination = base_address + i + 4 + relative_offset

        if destination in addresses:
            result[destination].append(base_address + i)

    return result


def invert_cross_reference_table(cross_references: Mapping[Rva, List[Rva]]) -> Mapping[Rva, Rva]:
    """
    Invert mapping from {Destination Rva: list of cross reverences} to {cross reference: destination}
    :param cross_references:
    :return: Mapping[source: Rva, destination: Rva] - inverted mapping
    """
    result = dict()
    for object_rva, references in cross_references.items():
        for ref in references:
            result[ref] = object_rva

    return result


def find_intersected_cross_references(cross_references: Mapping[Rva, List[Rva]]) -> Iterator[Tuple[Rva, Rva]]:
    """
    Find collisions of the references (i.e. when one supposed reference intersects with another one)
    :param cross_references: mapping of the cross-references
    :return: iterator of collisions
    """
    references = sorted(chain.from_iterable(cross_references.values()))

    for i, item in enumerate(references):
        j = i + 1
        while j < len(references) and references[j] - item < 4:
            yield item, references[j]
            j += 1
