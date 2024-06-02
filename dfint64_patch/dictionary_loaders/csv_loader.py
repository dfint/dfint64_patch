import csv
from collections.abc import Iterator
from typing import TextIO


def load_translation_file(fn: TextIO) -> Iterator[tuple[str, str]]:
    def unescape(string: str) -> str:
        return string.replace("\\r", "\r").replace("\\t", "\t")

    dialect = "unix"

    fn.seek(0)
    reader = csv.reader(fn, dialect)
    for source, translation, *_ in reader:
        yield unescape(source), unescape(translation)
