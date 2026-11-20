# Combination sum IV (ordered ways)

`nums` holds different positive numbers, and each one may be used any number of times. Write `ordered_ways(nums, target)` that returns how many **sequences** of numbers from `nums` add up to exactly `target` (chapter section 7, "Counting the ways (sequences, order matters)").

Here order **does** matter: `1 + 1 + 2`, `1 + 2 + 1` and `2 + 1 + 1` are three different sequences. This is the twin of p018, which counts each combination once.

## Example

```python
>>> ordered_ways([1, 2, 3], 4)
7
>>> ordered_ways([9], 3)
0
>>> ordered_ways([5], 0)          # the empty sequence
1
```

The 7 sequences for `[1, 2, 3]` and 4 are:

```text
1+1+1+1   1+1+2   1+2+1   2+1+1   2+2   1+3   3+1
```

For the same input, p018's `coin_ways([1, 2, 3], 4)` is 4: it counts `1+1+2`, `1+2+1` and `2+1+1` as one, and `1+3` and `3+1` as one.

## Constraints

- `1 <= len(nums) <= 10`, different values from 1 to 1000, in any order.
- `0 <= target <= 10**4`. Return the exact count (Python integers do not overflow, so the count can be very large).
- `O(target * len(nums))`.

## Think about

1. Think about the **last** number of a sequence that sums to `a`. If it is `x`, what is left in front of it, and how many ways are there to make that part?
2. In p018 the coins were the outer loop. Which loop has to be outside here, and why does that make the order count?
3. What is `f[0]`, and why is it not 0?
