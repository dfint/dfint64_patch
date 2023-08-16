import os
from contextlib import contextmanager
from shutil import copy

from loguru import logger


@contextmanager
def copy_source_file_context(src, dest, cleanup):
    logger.info(f"Copying '{src}'\nTo '{dest}'...")
    try:
        copy(src, dest)
    except OSError as ex:
        logger.info("Failed.")
        raise ex
    else:
        logger.info("Success.")

    try:
        yield dest
    except Exception as ex:
        if cleanup:
            logger.info(f"Removing '{dest}'")
            os.remove(dest)
        raise ex
