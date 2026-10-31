## Approach

The oracle is three lines and every run is tried, so its answer cannot be wrong in the clever ways the fast code can. One `@given`
test compares them on thousands of small lists: negative lists, lists with zeros, runs that start late, big last numbers,
a running sum of exactly -1. That single test catches five of the six bugs; the empty list is an error case with
no oracle answer, so it needs its own example test.

Small values (-10..10) and short lists (at most 12) matter: values near zero make running sums hit special
values like -1 and 0 often, and short lists keep the O(n^3) oracle fast and any failing example easy to read.

## Code

```python
import pytest
from hypothesis import given, settings, strategies as st

from target import max_subarray_sum


def slow_max_subarray_sum(nums):
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


def test_empty_list_is_an_error():
    with pytest.raises(ValueError):
        max_subarray_sum([])
```

## Cost

Oracle: O(n^3) per example, with n <= 12 and 100 examples: a few milliseconds in total. The tested function is O(n).

## Another way

Use `itertools.combinations(range(len(nums) + 1), 2)` to list the `(start, end)` pairs in one line. Or keep a few hand-picked
examples next to the oracle test: they document the tricky cases for the reader, and they fail first if the oracle itself has a bug.
