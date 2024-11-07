import contextlib
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest
from _pytest.capture import CaptureFixture

from dfint64_patch.extract_strings.cli import extract_strings, main
from dfint64_patch.extract_strings.from_raw_bytes import (
    ExtractedStringInfo,
    check_string,
    extract_strings_from_raw_bytes,
)
from dfint64_patch.type_aliases import Rva

from .utils import get_exe_stdout


@pytest.mark.parametrize(
    ("test_data", "encoding", "expected"),
    [
        (b"12345", "cp437", 0),
        (b"12345\xff", "utf-8", None),
        (b"1234abc5", "utf-8", 3),
    ],
)
def test_check_string(test_data: bytes, encoding: str, expected: tuple[int, int]):
    assert check_string(test_data) == expected


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
            {
                ExtractedStringInfo(Rva(8), "bc"),
                ExtractedStringInfo(Rva(12), "qwerty qwerty"),
                ExtractedStringInfo(Rva(28), "xyz"),
            },
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
            {
                ExtractedStringInfo(Rva(7), "abc"),
                ExtractedStringInfo(Rva(12), "qwerty qwerty"),
                ExtractedStringInfo(Rva(28), "xyz"),
            },
        ),
        (dict(bytes_block=b"12345\xff\0", encoding="utf-8"), set()),  # b"\xFF" cannot be decoded from utf-8 encoding
    ],
)
def test_extract_strings_from_raw_bytes(test_data: dict[str, Any], expected: set[ExtractedStringInfo]):
    assert set(extract_strings_from_raw_bytes(**test_data)) == expected


EXE_STRINGS = {
    "Hello, World!",
    "Unit report sheet popup",
}


@pytest.fixture
def exe_strings(exe_file_path: Path) -> set[str]:
    try:
        return set(get_exe_stdout(exe_file_path))
    except FileNotFoundError:
        return EXE_STRINGS


def test_exe_strings(exe_strings: set[str]):
    assert exe_strings, "Empty strings list"
    assert exe_strings <= EXE_STRINGS


def test_extract_string_cli(exe_file_path: Path, exe_strings: set[str]):
    with Path(exe_file_path).open("rb") as pe_file:
        strings = {x.string for x in extract_strings(pe_file)}
        assert strings >= exe_strings


def test_extract_strings_cli_2(exe_file_path: Path, exe_strings: set[str]):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_name = Path(temp_dir) / "string_dump.txt"
        with contextlib.suppress(SystemExit):
            sys.argv = [sys.argv[0], f"file_name={exe_file_path}", f"out_file={file_name}"]
            main()

        with Path(file_name).open() as file:
            strings = {line.rstrip() for line in file}

        assert strings >= exe_strings


def test_extract_strings_cli_3(exe_file_path: Path, capsys: CaptureFixture[str], exe_strings: set[str]):
    with contextlib.suppress(SystemExit):
        sys.argv = [sys.argv[0], f"file_name={exe_file_path}", "out_file=stdout"]
        main()

        strings = set(capsys.readouterr().out.splitlines())
        assert strings >= exe_strings
