import pytest
from hypothesis import given, settings, strategies as st

from target import max_subarray_sum


def slow_max_subarray_sum(nums):
    """Obviously correct, O(n^3): try every run and add it up."""
    best = None
    for start in range(len(nums)):
        for end in range(start + 1, len(nums) + 1):
            total = sum(nums[start:end])
            if best is None or total > best:
                best = total
    return best


small_lists = st.lists(st.integers(min_value=-10, max_value=10), min_size=1, max_size=12)


@settings(derandomize=True, database=None, max_examples=100)
@given(small_lists)
def test_fast_matches_slow(nums):
    assert max_subarray_sum(nums) == slow_max_subarray_sum(nums), (
        "The fast version must agree with the slow, obviously correct one.")


def test_known_cases():
    assert max_subarray_sum([2, -5, 3, 4]) == 7, "The best run is 3 + 4."
    assert max_subarray_sum([-3, -1, -2]) == -1, "All negative: the largest single number."


def test_empty_list_is_an_error():
    with pytest.raises(ValueError):
        max_subarray_sum([])
