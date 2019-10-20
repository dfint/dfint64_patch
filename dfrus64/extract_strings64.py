from pefile import PE


forbidden = set(b'$^')
allowed = set(b'\r\t')


def is_allowed(x: int):
    return x in allowed or (ord(' ') <= x and x not in forbidden)


def possible_to_decode(c, encoding):
    try:
        c.decode(encoding=encoding)
    except UnicodeDecodeError:
        return False
    else:
        return True


def check_string(buf: bytes, encoding):
    """
    Try to decode bytes as a string in the given encoding
    :param buf: byte buffer
    :param encoding: string encoding
    :return: string_length, number_of_letters
    """

    s_len = None
    letters = 0
    for i, c in enumerate(buf):
        if c == 0:
            s_len = i
            break

        if not is_allowed(c) or not possible_to_decode(buf[i:i + 1], encoding):
            break
        elif buf[i:i + 1].isalpha():
            letters += 1

    return s_len, letters


def extract_strings(bytes_block: bytes, base_address=0, alignment=4, encoding='cp437'):
    view = memoryview(bytes_block)
    strings = dict()

    i = 0
    while i < len(view):
        buffer_part = bytes(view[i:])
        string_len, letters = check_string(buffer_part, encoding)
        if string_len and letters:
            strings[base_address+i] = bytes(view[i: i+string_len]).decode(encoding)
            i += (string_len // alignment + 1) * alignment
            continue

        i += alignment
