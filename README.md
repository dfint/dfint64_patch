# DFRUS64

[![Test](https://github.com/dfint/dfrus64/actions/workflows/test.yml/badge.svg)](https://github.com/dfint/dfrus64/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/dfint/dfrus64/branch/master/graph/badge.svg?token=hDoXyRj4FB)](https://codecov.io/gh/dfint/dfrus64)
[![Maintainability](https://api.codeclimate.com/v1/badges/42d223b64187d6e7a05c/maintainability)](https://codeclimate.com/github/dfint/dfrus64/maintainability)

Text patcher for x64 bit version of the Dwarf Fortress game (work in progress).

You need python 3.7+ and poetry installed (`pip3 install poetry` or `pip install poetry`). Then run `poetry install` from the command line: it will create a virtual environment in the project's directory and install all the requirements into it. 

Basic usage examples:
```commandline
> poetry run extract --help
Usage: extract [OPTIONS] FILE_NAME [OUT_FILE]

Options:
  --sort-by-xref  Sort extracted strings by cross-reference
  --help          Show this message and exit.
```
```commandline
> poetry run patch --help
Usage: patch [OPTIONS] [SOURCE_FILE] [PATCHED_FILE]

Options:
  --dict TEXT        Path to the dictionary csv file
  --codepage TEXT    Enable support of the given codepage by name
  --cleanup BOOLEAN  Remove patched file on error
  --help             Show this message and exit.
```
```commandline
> poetry run patch_charmap --help
Usage: patch_charmap [OPTIONS] [SOURCE_FILE] [PATCHED_FILE] CODEPAGE

Options:
  --cleanup BOOLEAN  Remove patched file on error
  --help             Show this message and exit.
```
