## Hint 1

What is the most boring way to find the best run? Two nested loops: where does a run start, where does it end? For each pair, add
the numbers up and remember the largest total. Why does a boring version help? (It is easy to see that it is right.)

## Hint 2

The oracle needs a starting value for "best so far". Zero would be wrong for lists of only negative numbers, the very case the fast code can get
wrong. Use `None`, or the sum of the first run. Then write the `@given` test and a separate plain test for `[]`.

```
def slow(nums):
    best = None
    for start in range(len(nums)):
        for end in range(start + 1, len(nums) + 1):
            total = sum(nums[start:end])
            if best is None or total > best: best = total
    return best

@given(lists(integers(-10, 10), min_size=1, max_size=12))  assert fast(nums) == slow(nums)
def test_empty(): with pytest.raises(ValueError): fast([])
```
