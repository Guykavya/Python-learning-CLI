# Save the code from problem.md as target.py in this folder to try your tests:
#     python -m pytest solution.py
from hypothesis import given, settings, strategies as st

from target import decode, encode


@settings(derandomize=True, database=None, max_examples=100)
@given(st.text(alphabet="abc"))
def test_decode_undoes_encode(text):
    assert decode(encode(text)) == text
