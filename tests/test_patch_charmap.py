import pytest

from dfrus64.patch_charmap import Encoder, ord_utf16, get_encoder


@pytest.mark.parametrize('codepage_data,input_string,expected', [
    ({0x1E: ord_utf16('Ỵ'), 0x80: map(ord_utf16, 'ẠẮẰẶẤẦẨẬẼẸẾỀỂỄỆỐ')}, 'ẠẮẰỴ ', b'\x80\x81\x82\x1E ')
])
def test_encoder(codepage_data, input_string, expected):
    encoder = Encoder(codepage_data)
    assert encoder.encode(input_string) == (expected, len(expected))


def test_combining_grave_accent():
    text = 'ờ'
    assert get_encoder('viscii')(text)[0]
