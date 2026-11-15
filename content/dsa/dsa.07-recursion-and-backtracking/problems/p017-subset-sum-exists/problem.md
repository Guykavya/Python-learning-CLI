# Subset sum: does one exist?

Write `has_subset_sum(nums, target)` that returns `True` if **some** subset of `nums` (any items, each position used at most once) adds up to exactly `target`, and `False` otherwise.

- The empty subset has sum 0, so `target == 0` is always `True`.
- Numbers may be negative, zero or positive.

Use backtracking with an **early exit**: as soon as one subset works, stop searching and return `True` all the way up (chapter section 9, "Stop at the first answer").

## Example

```python
>>> has_subset_sum([3, 34, 4, 12, 5, 2], 9)
True
>>> has_subset_sum([3, 34, 4, 12, 5, 2], 30)
False
>>> has_subset_sum([-3, 1, 7], 4)
True
```

## Constraints

- `0 <= len(nums) <= 40`
- When the answer is `False`, `len(nums) <= 18`. When there are many items, a solution exists and the search must stop early.

## Think about

Because numbers can be negative, a sum that is already above the target can still come back down. Which pruning from the chapter is therefore **not** allowed here? Which check still is?
