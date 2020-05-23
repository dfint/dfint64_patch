from .type_aliases import Offset


def read_bytes(file_object, off: Offset, count=1) -> bytes:
    file_object.seek(off)
    return file_object.read(count)


def put_integer32(file_object, val):
    file_object.write(val.to_bytes(4, byteorder='little'))


def write_dwords(file_object, offset, dwords):
    file_object.seek(offset)
    for x in dwords:
        put_integer32(file_object, x)


def to_dword(x, signed=False, byteorder='little'):
    return x.to_bytes(length=4, byteorder=byteorder, signed=signed)


def write_string(file_object, s: str, off=None, new_len=None, encoding=None):
    if off is not None:
        file_object.seek(off)

    if new_len is None:
        new_len = len(s) + 1

    if encoding is None:
        s = s.encode()
    else:
        s = s.encode(encoding)

    file_object.write(s.ljust(new_len, b'\0'))
