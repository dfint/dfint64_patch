import csv
import io
import string
from typing import List, Tuple

from hypothesis import example, given
from hypothesis import strategies as st

from dfint64_patch.dictionary_loaders.csv_loader import load_translation_file

text_strategy = st.text(alphabet=string.printable).filter(lambda text: not ("\\r" in text or "\\t" in text))
translation_strategy = text_strategy


@given(st.lists(st.tuples(text_strategy, translation_strategy)))
@example([("\tsome\rtext", "\tкакой-то\rтекст")])
def test_load_translation_file(dictionary: List[Tuple[str, str]]):
    file = io.StringIO()
    csv_writer = csv.writer(file, dialect="unix")

    def escape(x: str):
        return x.replace("\r", "\\r").replace("\t", "\\t")

    for text, translation in dictionary:
        csv_writer.writerow((escape(text), escape(translation)))

    file.seek(0)

    assert list(load_translation_file(file)) == dictionary
