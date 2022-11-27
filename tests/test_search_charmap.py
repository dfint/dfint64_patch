from hypothesis import given
from hypothesis import strategies as st

from dfrus64.charmap.search_charmap import search_charmap, unicode_table_start


@given(st.binary().filter(lambda x: unicode_table_start not in x))
def test_search_charmap(head):
    assert search_charmap(head) is None
    assert search_charmap(head + unicode_table_start) == len(head)
