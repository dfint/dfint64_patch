import csv
import io
import string
from typing import List, Tuple

from hypothesis import given, example
from hypothesis import strategies as st

from dfrus64.dictionary_loaders.csv_loader import load_translation_file

valid_text = st.text(alphabet=string.printable)
valid_translation = valid_text


@given(st.lists(st.tuples(valid_text, valid_translation)))
@example([("\tsome\rtext", "\tкакой-то\rтекст")])
def test_load_translation_file(dictionary: List[Tuple[str, str]]):
    file = io.StringIO()
    csv_writer = csv.writer(file, dialect="unix")

    def escape(x: str):
        return x.replace("\r", "\\r").replace("\t", "\\t")

    for text, translation in dictionary:
        csv_writer.writerow((escape(text), escape(translation)))

    file.seek(0)

    assert list(load_translation_file(file)) == dictionary, (dictionary, file.getvalue())
