import pytest

from dfrus64.cross_references import *


@pytest.mark.parametrize('test_data,expected', [
    (dict(bytes_block=b'\0'*4, base_address=0, addresses=[4]), {4: [0]}),
    (dict(bytes_block=0x1000.to_bytes(byteorder='little', length=4) + b'\0'*4,
          base_address=0x10000, addresses=[0x11004]),
     {0x11004: [0x10000]}),
    # TODO: more tests
])
def test_find_relative_cross_references(test_data, expected):
    assert find_relative_cross_references(**test_data) == expected
