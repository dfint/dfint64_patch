import os
from contextlib import contextmanager
from shutil import copy

from loguru import logger


@contextmanager
def copy_source_file_context(src, dest, cleanup):
    logger.info("Copying '{}'\nTo '{}'...".format(src, dest))
    try:
        copy(src, dest)
    except IOError as ex:
        logger.info("Failed.")
        raise ex
    else:
        logger.info("Success.")

    try:
        yield dest
    except Exception as ex:
        if cleanup:
            logger.info("Removing '{}'".format(dest))
            os.remove(dest)
        raise ex
