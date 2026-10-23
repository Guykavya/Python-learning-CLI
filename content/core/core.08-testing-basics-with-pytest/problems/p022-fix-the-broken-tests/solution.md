## Approach

Each of the six faults has a different symptom, which is why each needs a different eye:

1. `test_median_even`: the expected value is wrong. The median of 1, 2, 3, 4 is (2 + 3) / 2 = **2.5**. This is the only fault that makes a test visibly fail.
2. Two functions named `test_median_odd`: the second definition replaces the first, so the first never runs. Silent.
3. `assert (median([5]) == 5, "...")` asserts a tuple, which is always true. Silent.
4. `test_unsorted` calls `median` and never checks the answer. Silent, and it was the only test of unsorted input.
5. `with pytest.raises(ValueError)` contains two calls. `median([1])` does not raise, so the test fails, but even if it did, `median([])` would never run.
6. `tset_negative` is a typo: pytest does not collect it. Silent.

## Code

```python
import pytest

from target import median


def test_median_odd():
    assert median([3, 1, 2]) == 2, "The middle of 1, 2, 3 is 2."


def test_median_odd_longer():
    assert median([9, 7, 8, 10, 6]) == 8, "Sorted: 6 7 8 9 10, the middle is 8."


def test_median_even():
    assert median([1, 2, 3, 4]) == 2.5, "Even count: the mean of the two middle values, (2 + 3) / 2."


def test_single():
    assert median([5]) == 5, "One number is its own median."


def test_unsorted():
    assert median([5, 1, 4]) == 4, "The input is not sorted: sort first. Sorted it is 1 4 5."


def test_empty():
    with pytest.raises(ValueError):
        median([])


def test_negative():
    assert median([-5, -1, -3]) == -3, "Sorted: -5 -3 -1, the middle is -3."
```

## Complexity

Not applicable.

## Another way

Delete the fragile tests and rewrite from scratch with `parametrize`. Fixing a file you did not write is a different skill from writing one: look for what is silently not running.
