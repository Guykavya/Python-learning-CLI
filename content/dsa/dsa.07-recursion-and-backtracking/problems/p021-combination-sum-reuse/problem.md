# Combination sum (reuse allowed)

Given a list of **distinct positive** integers `candidates` and a positive `target`, return all the different combinations of candidates whose sum is `target`. Each candidate may be used **any number of times**.

Two combinations are the same if they use the same numbers the same number of times, in any order: `[2, 2, 3]` and `[3, 2, 2]` count once. The order of the combinations and the order inside each combination do not matter (the tests sort).

## Example

```python
>>> combination_sum([2, 3, 6, 7], 7)
[[2, 2, 3], [7]]
>>> combination_sum([2, 3, 5], 8)
[[2, 2, 2, 2], [2, 3, 3], [3, 5]]
>>> combination_sum([4, 6], 3)
[]
```

## Constraints

- `1 <= len(candidates) <= 30`, `2 <= candidates[i] <= 40`, all different, `1 <= target <= 40`.
- The input may be in any order.

## Think about

How do you avoid producing `[2, 3, 2]` as well as `[2, 2, 3]`? And after choosing `candidates[i]`, should the next call start at `i` or at `i + 1`?
