import re
from collections.abc import Iterator
from typing import NamedTuple

SUBROUTINE_ALIGNMENT = 4


class SubroutineInfo(NamedTuple):
    start: int
    end: int  # exclusive


def extract_subroutines(buffer: bytes) -> Iterator[SubroutineInfo]:
    start = 0

    for match in re.finditer(rb"\xCC+", buffer):
        if match.end() % SUBROUTINE_ALIGNMENT != 0:
            continue

        end = match.start()
        yield SubroutineInfo(start, end)
        start = match.end()

    if start < len(buffer):
        yield SubroutineInfo(start, len(buffer))
