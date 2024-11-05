from pathlib import Path

import click
from loguru import logger

from dfint64_patch.backup import copy_source_file_context
from dfint64_patch.dictionary_loaders.csv_loader import load_translation_file
from dfint64_patch.patching.patch import patch


@click.command()
@click.argument(
    "source_file",
    default="Dwarf Fortress.exe",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
)
@click.argument("patched_file", default="Dwarf Fortress Patched.exe")
@click.option("--dict", "dictionary_file", help="Path to the dictionary csv file")
@click.option("--encoding", "encoding", help="Encoding for the translation", default="cp437")
@click.option("--cleanup", "cleanup", help="Remove patched file on error", default=False)
def main(source_file: str, patched_file: str, dictionary_file: str, encoding: str, cleanup: bool) -> None:  # noqa: FBT001
    with copy_source_file_context(source_file, patched_file, cleanup=cleanup):
        logger.info("Loading translation file...")

        with Path(dictionary_file).open(encoding="utf-8") as trans:
            translation_table = list(load_translation_file(trans))

        print(source_file)  # TODO: split translation table for debugging

        patch(patched_file, translation_table, encoding)


if __name__ == "__main__":
    main()
