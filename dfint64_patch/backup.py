from collections.abc import Generator
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from shutil import copy

from loguru import logger


@contextmanager
def copy_source_file_context(src: PathLike[str], dest: PathLike[str], *, cleanup: bool) -> Generator[PathLike[str]]:
    """
    Context manager to backup file and restore it on exit (if needed)
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
