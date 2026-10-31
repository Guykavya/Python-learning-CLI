# Save the code from problem.md as target.py in this folder to try your tests:
#     python -m pytest solution.py
from hypothesis import given, settings, strategies as st

from target import reverse, sorted_copy


@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers()))
def test_reverse_twice_is_the_original(xs):
    assert reverse(reverse(xs)) == xs
