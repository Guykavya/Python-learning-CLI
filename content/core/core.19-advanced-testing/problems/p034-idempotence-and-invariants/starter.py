# Save the code from problem.md as target.py in this folder to try your tests:
#     python -m pytest solution.py
from hypothesis import given, settings, strategies as st

from target import dedupe, normalise_whitespace, sort_by_length


@settings(derandomize=True, database=None, max_examples=100)
@given(st.text())
def test_normalise_is_idempotent(text):
    once = normalise_whitespace(text)
    assert normalise_whitespace(once) == once
