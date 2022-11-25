from io import BytesIO

from dfrus64.binio import *


def test_binio():
    file_object = BytesIO()

    write_dword(file_object, 0xDEADBEEF)
    write_string(file_object, "1234")

    assert read_bytes(file_object, 0, 9) == b"\xef\xbe\xad\xde1234\x00"
