import string

import pytest

from . import utils
from .utils import get_random_string


@pytest.mark.parametrize("length", range(33))
def test_get_random_string(length: int):
    generated_string = get_random_string(length)
    if length == 0:
        assert generated_string == ""
        return

    words = generated_string.split(" ")

    assert len(generated_string) == length
    assert generated_string == generated_string.strip()
    assert all(words)
    assert all(set(word) <= set(string.ascii_lowercase) for word in words)


def test_get_random_string_avoids_not_equals(monkeypatch: pytest.MonkeyPatch):
    generated_words = iter(["abc", "x", "def", "x"])
    monkeypatch.setattr(utils, "get_random_word", lambda _: next(generated_words))

    assert get_random_string(3, not_equals="abc") == "def"


def test_get_random_string_retries_when_truncated_at_separator(monkeypatch: pytest.MonkeyPatch):
    generated_words = iter(["ab", "c", "d", "ef"])
    monkeypatch.setattr(utils, "get_random_word", lambda _: next(generated_words))

    assert get_random_string(3) == "d e"


def test_get_random_string_bounds_separator_retries(monkeypatch: pytest.MonkeyPatch):
    generated_words = ["ab", "c"]
    calls = 0

    def get_separator_ending_word(_: int) -> str:
        nonlocal calls
        word = generated_words[calls % len(generated_words)]
        calls += 1
        return word

    monkeypatch.setattr(utils, "get_random_word", get_separator_ending_word)

    with pytest.raises(ValueError, match="Infinite loop"):
        get_random_string(3)

    assert calls == utils._MAX_RETRIES * len(generated_words)  # noqa: SLF001
