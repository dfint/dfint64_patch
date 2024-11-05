import pytest

from dfint64_patch.extract_subroutines.from_raw_bytes import SubroutineInfo, extract_subroutines, which_subroutine


@pytest.mark.parametrize(
    ("test_data", "offset", "expected"),
    [
        (b"\x90" * 8, 0, [SubroutineInfo(0, 8)]),
        (b"\x90\xcc", 0, [SubroutineInfo(0, 2)]),
        (b"\x90\xcc\xcc\xcc\x90\x90", 0, [SubroutineInfo(0, 1), SubroutineInfo(4, 6)]),
        (b"\x90\xcc\xcc\xcc\x90\x90", 1, [SubroutineInfo(1, 2), SubroutineInfo(5, 7)]),
    ],
)
def test_extract_subroutines_from_bytes(test_data: bytes, offset: int, expected: list[SubroutineInfo]):
    assert list(extract_subroutines(test_data, offset)) == expected


@pytest.mark.parametrize(
    ("subroutines", "address", "expected"),
    [
        ([], 0, None),
        ([SubroutineInfo(1, 2)], 2, None),
        ([SubroutineInfo(1, 2)], 0, None),
        ([SubroutineInfo(1, 2), SubroutineInfo(3, 4)], 2, None),
        ([SubroutineInfo(1, 2)], 1, SubroutineInfo(1, 2)),
        ([SubroutineInfo(1, 2), SubroutineInfo(3, 4), SubroutineInfo(4, 5)], 3, SubroutineInfo(3, 4)),
    ],
)
def test_which_subroutine(subroutines: list[SubroutineInfo], address: int, expected: bool):
    assert which_subroutine(subroutines, address) == expected
