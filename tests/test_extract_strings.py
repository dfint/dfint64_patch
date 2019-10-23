import pytest

from dfrus64.extract_strings import *


@pytest.mark.parametrize('test_data,encoding,expected', [
    (b'12345\0', 'cp437', (5, 0)),
    (b'12345\xFF\0', 'utf-8', (0, 0)),
])
def test_check_string(test_data, encoding, expected):
    assert check_string(test_data, encoding) == expected


@pytest.mark.parametrize('test_data,expected', [
    (dict(bytes_block=b'\0' * 7 + b'a' +  # b'a' must be ignored because it not aligned properly
                      b'bc'.ljust(4, b'\0') +
                      b'qwerty qwerty'.ljust(16, b'\0') +
                      b'xyz\0'),
     {8: 'bc', 12: 'qwerty qwerty', 28: 'xyz'}),
    (dict(alignment=1,
          bytes_block=b'\0' * 7 + b'a' +  # b'a' must not be ignored
                      b'bc'.ljust(4, b'\0') +
                      b'qwerty qwerty'.ljust(16, b'\0') +
                      b'xyz\0'),
     {7: 'abc', 12: 'qwerty qwerty', 28: 'xyz'}),
    (dict(bytes_block=b'12345\xFF\0', encoding='utf-8'), dict()),  # b'\xFF' cannot be decoded from utf-8 encoding
])
def test_extract_strings_from_raw_bytes(test_data, expected):
    assert extract_strings_from_raw_bytes(**test_data) == expected
