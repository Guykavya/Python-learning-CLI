# Oracle testing: fast against slow

Sometimes you cannot state a neat property, but you *can* write a slow version that is
obviously right. Then the property is "the fast version agrees with the slow one on every input".
The slow version is called an **oracle**.

```python
def max_subarray_sum(nums):
    """Largest sum of a non-empty run of neighbouring numbers (Kadane's algorithm).

    max_subarray_sum([2, -5, 3, 4]) == 7. All numbers negative: the best run is the single
    largest number. An empty list raises ValueError.
    """
    if not nums:
        raise ValueError("nums must not be empty")
    best = current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return best
```

The fast algorithm above is clever, and clever code hides bugs. In `solution.py`:

1. Write the oracle `slow_max_subarray_sum(nums)`: try **every** run `nums[start:end]`, add it up with `sum`, keep the largest. No cleverness.
2. Write a `@given` test that compares `max_subarray_sum` with your oracle. Keep inputs small
   (`st.lists(st.integers(-10, 10), min_size=1, max_size=12)`): the oracle is slow and small inputs shrink well.
3. Add a test for the empty list (`pytest.raises(ValueError)`).

Import with `from target import max_subarray_sum` (save the code above as `target.py` to try your tests).
Put `@settings(derandomize=True, database=None, max_examples=100)` above every `@given`.

Your tests must **pass** on the correct code and **fail** on each of six buggy versions. The report names the survivors.

**How this is checked.** Your `solution.py` is copied next to the code above (saved as `target.py`)
and real pytest runs on it: first on the correct code, then on each buggy copy. At least one test must fail on each bug.

**Example of the shape of the test**

```python
@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers(-10, 10), min_size=1, max_size=12))
def test_fast_matches_slow(nums):
    assert max_subarray_sum(nums) == slow_max_subarray_sum(nums), "fast and slow must agree."
```
