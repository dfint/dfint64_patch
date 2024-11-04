import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, TextIO


@contextmanager
def maybe_open(file_name: str | None) -> Generator[TextIO, None, None]:
    """
    Open a file if the name is provided, and close it on exit from with-block,
    or provide stdout as a file object, if the file_name parameter is None
    :param file_name: file name or None
    :return: file object
    """
    file_object = sys.stdout if file_name is None or file_name == "stdout" else Path(file_name).open("w")  # noqa: SIM115

    try:
        yield file_object
    finally:
        if file_object != sys.stdout:
            file_object.close()
