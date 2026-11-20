# Subset sum

Write `subset_sum(nums, target)` that returns `True` if some subset of `nums` (each element used **at most once**) adds up to exactly `target`, and `False` otherwise (chapter section 12). The empty subset sums to 0.

## Example

```python
>>> subset_sum([3, 34, 4, 12, 5, 2], 9)     # 4 + 5
True
>>> subset_sum([3, 34, 4, 12, 5, 2], 30)
False
>>> subset_sum([2], 4)                      # 2 + 2 would reuse the same element
False
>>> subset_sum([], 0)
True
```

## Constraints

- `0 <= len(nums) <= 300`; every number from 0 to 10**4.
- `0 <= target <= 10**4`.
- `O(len(nums) * target)` time, `O(target)` memory.

## Bonus (optional)

Also write `subset_sum_bits(nums, target)` using the big-integer trick of chapter section 12: bit `s` of one integer is 1 when the sum `s` is reachable. The bonus test gives it 2,000 numbers and a target of 10**5, which is far too slow for a list loop in Python. If you do not write it, that test is **skipped**, not failed.

## Think about

1. This is a 0/1 knapsack where the "value" is just yes or no. What is `f[s]`, and what is `f[0]`?
2. With one list, which direction must the `s` loop go so that each number is used at most once?
3. In the bit version, what does `bits << x` mean in words? Why does `bits | (bits << x)` add the number `x` to every reachable sum at once?
