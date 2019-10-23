
from .cross_references import find_relative_cross_references
from .extract_strings import extract_strings_from_raw_bytes

import click
import pefile


@click.argument('file_name')
def main(file_name):
    pass


if __name__ == '__main__':
    main()
