# Combination sum II (each number once)

Given a list `candidates` of positive integers **that may contain repeated values**, and a positive `target`, return all different combinations whose sum is `target`. Each **position** may be used at most once, but the result must not contain the same combination twice.

For `[10, 1, 2, 7, 6, 1, 5]` and target 8, `[1, 1, 6]` is allowed (two different 1s), but `[1, 7]` must appear only once even though there are two 1s that could be used.

## Example

```python
>>> combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)
[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
>>> combination_sum2([2, 5, 2, 1, 2], 5)
[[1, 2, 2], [5]]
```

The tests sort before comparing.

## Constraints

- `1 <= len(candidates) <= 100`, `1 <= candidates[i] <= 50`, `1 <= target <= 30`.

## Think about

Removing duplicates at the end with a `set` is correct but can be very slow: `[1] * 30` with target 15 has 155,117,520 position-subsets but only one answer. Prevent the duplicates **while** searching (chapter section 7).
