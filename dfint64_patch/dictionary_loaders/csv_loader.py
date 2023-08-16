import csv
from collections.abc import Iterator
from typing import TextIO


def load_translation_file(fn: TextIO) -> Iterator[tuple[str, str]]:
    def unescape(x):
        return x.replace("\\r", "\r").replace("\\t", "\t")

    dialect = "unix"

    fn.seek(0)
    reader = csv.reader(fn, dialect)
    for parts in reader:
        assert len(parts) >= 2, parts
        yield unescape(parts[0]), unescape(parts[1])
