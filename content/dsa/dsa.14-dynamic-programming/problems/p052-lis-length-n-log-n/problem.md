# LIS length in O(n log n)

Same question as p051: the length of the longest **strictly increasing** subsequence. But now the list has up to **100,000** numbers, and the `O(n^2)` table would need 5 billion steps. Write `lis_len(nums)` in `O(n log n)` with the `tails` method of chapter section 13 and the `bisect` module.

## Example

```python
>>> lis_len([10, 9, 2, 5, 3, 7, 101, 18])
4
>>> lis_len([4, 10, 4, 3, 8, 9])     # for example 4, 8, 9
3
>>> lis_len([2, 2, 3, 3, 1])         # strictly increasing: 2, 3
2
>>> lis_len([])
0
```

## Constraints

- `0 <= len(nums) <= 10**5`, integers, possibly with many repeats.
- Time `O(n log n)`. The test gives 100,000 numbers with a time limit; an `O(n^2)` solution does not finish.

## Think about

`tails[k]` is the **smallest possible last value** of an increasing subsequence of length `k + 1` seen so far. Why is `tails` always sorted? For a new number `x`, which position does `bisect_left(tails, x)` find, and why must an `x` that is **equal** to some `tails[k]` replace it rather than extend the list?
