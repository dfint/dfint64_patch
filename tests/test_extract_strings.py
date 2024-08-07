import contextlib
import io
import tempfile
from pathlib import Path

import pytest

from dfint64_patch.extract_strings.cli import extract_strings, main
from dfint64_patch.extract_strings.from_raw_bytes import (
    check_string,
    extract_strings_from_raw_bytes,
)


@pytest.mark.parametrize(
    ("test_data", "encoding", "expected"),
    [
        (b"12345\0", "cp437", (5, 0)),
        (b"12345\xff\0", "utf-8", (0, 0)),
    ],
)
def test_check_string(test_data: bytes, encoding: str, expected: tuple[int, int]):
    assert check_string(test_data, encoding) == expected


@pytest.mark.parametrize(
    ("test_data", "expected"),
    [
        (
            dict(
                bytes_block=b"\0" * 7
                + b"a"  # b"a" must be ignored because it is not aligned properly
                + b"bc".ljust(4, b"\0")
                + b"qwerty qwerty".ljust(16, b"\0")
                + b"xyz\0",
            ),
            {8: "bc", 12: "qwerty qwerty", 28: "xyz"},
        ),
        (
            dict(
                alignment=1,
                bytes_block=b"\0" * 7
                + b"a"
                + b"bc".ljust(4, b"\0")  # b"a" must not be ignored
                + b"qwerty qwerty".ljust(16, b"\0")
                + b"xyz\0",
            ),
            {7: "abc", 12: "qwerty qwerty", 28: "xyz"},
        ),
        (dict(bytes_block=b"12345\xff\0", encoding="utf-8"), {}),  # b"\xFF" cannot be decoded from utf-8 encoding
    ],
)
def test_extract_strings_from_raw_bytes(test_data: dict, expected: dict):
    assert dict(extract_strings_from_raw_bytes(**test_data)) == expected


EXE_STRINGS = {
    "Hello, World!",
    "Unit report sheet popup",
}


def test_extract_string_cli():
    exe_file_path = Path(__file__).parent / "test64.exe"
    with Path(exe_file_path).open("rb") as pe_file:
        strings = {x.string for x in extract_strings(pe_file)}
        assert strings >= EXE_STRINGS


def test_extract_strings_cli_2():
    exe_file_path = Path(__file__).parent / "test64.exe"
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = Path(temp_dir) / "string_dump.txt"
        with contextlib.suppress(SystemExit):
            main([str(exe_file_path), str(file_name)])

        with Path(file_name).open() as file:
            strings = {line.rstrip() for line in file}

        assert strings >= EXE_STRINGS


def test_extract_strings_cli_3():
    exe_file_path = Path(__file__).parent / "test64.exe"
    stdout = io.StringIO()

    with contextlib.redirect_stdout(stdout):
        with contextlib.suppress(SystemExit):
            main([str(exe_file_path)])

        strings = set(stdout.getvalue().splitlines())
        assert strings >= EXE_STRINGS
