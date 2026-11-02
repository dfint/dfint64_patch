import string

import pytest

from . import utils
from .utils import get_random_string


@pytest.mark.parametrize("length", range(1, 33))
def test_get_random_string(length: int):
    generated_string = get_random_string(length)
    words = generated_string.split(" ")

    assert len(generated_string) == length
    assert generated_string == generated_string.strip()
    assert all(words)
    assert all(set(word) <= set(string.ascii_lowercase) for word in words)


def test_get_random_string_retries_when_truncated_at_separator(monkeypatch: pytest.MonkeyPatch):
    generated_words = iter(["ab", "c", "d", "ef"])
    monkeypatch.setattr(utils, "get_random_word", lambda _: next(generated_words))

    assert get_random_string(3) == "d e"
