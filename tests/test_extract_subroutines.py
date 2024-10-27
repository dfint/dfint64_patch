import pytest

from dfint64_patch.extract_subroutines.from_raw_bytes import SubroutineInfo, extract_subroutines


@pytest.mark.parametrize(
    ("test_data", "expected"),
    [
        (b"\x90" * 8, [SubroutineInfo(0, 8)]),
        (b"\x90\xCC", [SubroutineInfo(0, 2)]),
        (b"\x90\xCC\xCC\xCC\x90\x90", [SubroutineInfo(0, 1), SubroutineInfo(4, 6)]),
    ],
)
def test_extract_subroutines_from_bytes(test_data: bytes, expected: list[SubroutineInfo]):
    assert list(extract_subroutines(test_data)) == expected
