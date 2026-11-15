# All permutations

Write `permute(nums)` that returns all permutations (orderings) of the list `nums`, whose items are all different. Each permutation is a list. The order of the permutations in your result does not matter (the tests sort them).

Use backtracking with a `used` list (chapter section 8). `itertools` is not allowed.

## Example

```python
>>> sorted(permute([1, 2, 3]))
[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
>>> permute([])
[[]]
```

## Constraints

- `0 <= len(nums) <= 8`, all items different. Do not change `nums`.

## Think about

Why can you not use a `start` index here, as in subsets? Any unused item may come next.
