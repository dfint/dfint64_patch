from collections.abc import Generator
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from shutil import copy
from typing import TypeVar

from loguru import logger

T = TypeVar("T", bound=str | PathLike)


@contextmanager
def copy_source_file_context(src: str | PathLike, dest: T, *, cleanup: bool) -> Generator[T, None, None]:
    """
    Context manager to back up file and restore it on exit (if needed)
    """
    logger.info(f"Copying '{src}'\nTo '{dest}'...")
    try:
        copy(src, dest)
    except OSError:
        logger.info("Failed.")
        raise
    else:
        logger.info("Success.")

    try:
        yield dest
    except Exception:
        if cleanup:
            logger.info(f"Removing '{dest}'")
            Path(dest).unlink()
        raise
