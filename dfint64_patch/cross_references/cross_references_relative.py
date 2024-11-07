from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping
from itertools import chain

from tqdm import tqdm

from dfint64_patch.type_aliases import Rva

REFERENCE_SIZE = 4


def find_relative_cross_references_low(
    bytes_block: bytes, base_address: Rva, addresses: Iterable[int]
) -> Iterator[tuple[int, int]]:
    for i in range(len(bytes_block) - REFERENCE_SIZE + 1):
        relative_offset = int.from_bytes(bytes_block[i : i + REFERENCE_SIZE], byteorder="little", signed=True)
        destination = base_address + i + REFERENCE_SIZE + relative_offset

        if destination in addresses:
            yield destination, base_address + i


def find_relative_cross_references(
    bytes_block: bytes,
    base_address: Rva,
    addresses: Iterable[Rva],
) -> Mapping[Rva, list[Rva]]:
    """
    Analyse a block of bytes and try to find relative cross-references to the given objects' addresses
    :param bytes_block: bytes block to analyse
    :param base_address: base address of the given block
    :param addresses: an iterable of addresses. In addition to list and other flat types it also can be range
        (e.g. `range(0x11000, 0x12000)`) or dict object.
    :return: Mapping[object_rva: Rva, cross_references: List[Rva]]
    """
    result = defaultdict(list)

    if not isinstance(addresses, range | dict):
        addresses = set(addresses)

    for destination, source in tqdm(
        find_relative_cross_references_low(bytes_block, base_address, addresses),
        desc="find_relative_cross_references",
    ):
        result[destination].append(source)

    return result


def invert_cross_reference_table(cross_references: Mapping[Rva, list[Rva]]) -> Mapping[Rva, Rva]:
    """
    Invert mapping from {Destination Rva: [cross-reverence Rva]} to {cross-reference Rva: Destination Rva}
    :param cross_references: mapping of the cross-references
    :return: Mapping[source: Rva, destination: Rva] - inverted mapping
    """
    result = {}
    for object_rva, references in cross_references.items():
        for ref in references:
            result[ref] = object_rva

    return result


def find_intersected_cross_references(cross_references: Mapping[Rva, list[Rva]]) -> Iterator[tuple[Rva, Rva]]:
    """
    Find collisions of the references (i.e. when one supposed reference intersects with another one)
    :param cross_references: mapping of the cross-references
    :return: iterator of collisions
    """
    references = sorted(chain.from_iterable(cross_references.values()))

    for i, item in enumerate(references):
        j = i + 1
        while j < len(references) and references[j] - item < REFERENCE_SIZE:
            yield item, references[j]
            j += 1
