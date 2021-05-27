import pytest

from dfrus64.patch_charmap import Encoder, ord_utf16, get_encoder, get_codepages


@pytest.mark.parametrize('codepage_data,input_string,expected', [
    ({0x1E: ord_utf16('Ỵ'), 0x80: map(ord_utf16, 'ẠẮẰẶẤẦẨẬẼẸẾỀỂỄỆỐ')}, 'ẠẮẰỴ ', b'\x80\x81\x82\x1E ')
])
def test_encoder(codepage_data, input_string, expected):
    encoder = Encoder(codepage_data)
    assert encoder.encode(input_string) == (expected, len(expected))


def test_combining_grave_accent():
    text = 'ờ'
    assert get_encoder('viscii')(text)[0]


def test_get_codepages():
    for codepage in get_codepages():
        assert codepage in {'cp437', 'viscii'} or int(codepage[2:]) in range(700, 1253)
