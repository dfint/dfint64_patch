import re
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from typing import NamedTuple

SUBROUTINE_ALIGNMENT = 4


class SubroutineInfo(NamedTuple):
    start: int
    end: int  # exclusive


def extract_subroutines(buffer: bytes, base_offset: int = 0) -> Iterator[SubroutineInfo]:
    start = 0

    for match in re.finditer(rb"\xCC+", buffer):
        if match.end() % SUBROUTINE_ALIGNMENT != 0:
            continue

        end = match.start()
        yield SubroutineInfo(base_offset + start, base_offset + end)
        start = match.end()

    if start < len(buffer):
        yield SubroutineInfo(base_offset + start, base_offset + len(buffer))


def which_subroutine(subroutines: Sequence[SubroutineInfo], address: int) -> SubroutineInfo | None:
    addresses = [subroutine.start for subroutine in subroutines]
    index = bisect_right(addresses, address) - 1
    if index < 0 or index >= len(subroutines) or address >= subroutines[index].end:
        return None
    return subroutines[index]
