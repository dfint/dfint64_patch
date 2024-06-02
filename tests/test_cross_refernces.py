import pytest

from dfint64_patch.cross_references.cross_references_relative import (
    find_intersected_cross_references,
    find_relative_cross_references,
    invert_cross_reference_table,
)


@pytest.mark.parametrize(
    "test_data,expected",
    [
        (dict(bytes_block=b"\0" * 4, base_address=0, addresses=[4]), {4: [0]}),
        (
            dict(
                bytes_block=0x1000.to_bytes(byteorder="little", length=4) + b"\0" * 4,
                base_address=0x10000,
                addresses=[0x11004],
            ),
            {0x11004: [0x10000]},
        ),
        (
            dict(
                bytes_block=0x1000.to_bytes(byteorder="little", length=4) + b"\0" * 4,
                base_address=0x10000,
                addresses=range(0x11000, 0x12000),
            ),
            {0x11004: [0x10000]},
        ),
        # TODO: more tests
    ],
)
def test_find_relative_cross_references(test_data, expected):
    assert find_relative_cross_references(**test_data) == expected


@pytest.mark.parametrize(
    "test_data,expected", [({111: [222, 333, 444], 555: [0]}, {222: 111, 333: 111, 444: 111, 0: 555})],
)
def test_invert_cross_reference_table(test_data, expected):
    assert invert_cross_reference_table(test_data) == expected


@pytest.mark.parametrize(
    "test_data,expected",
    [({111: [0, 4, 8, 9], 222: [1, 2, 10]}, [(0, 1), (0, 2), (1, 2), (1, 4), (2, 4), (8, 9), (8, 10), (9, 10)])],
)
def test_find_intersected_cross_references(test_data, expected):
    assert list(find_intersected_cross_references(test_data)) == expected
