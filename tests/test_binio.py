from io import BytesIO

from dfrus64.binio import *


def test_binio():
    file_object = BytesIO()

    put_integer32(file_object, 0xDEADBEEF)
    write_string(file_object, "1234")

    assert file_object.getvalue() == b'\xef\xbe\xad\xde1234\x00'
