# Target sum (+/-)

Put a `+` or a `-` in front of **every** number of `nums`, then add everything up. Write `target_sum(nums, target)` that returns **how many** sign choices give exactly `target` (chapter section 12, "Target sum").

## Example

```python
>>> target_sum([1, 1, 1, 1, 1], 3)
5
>>> target_sum([1], 1)
1
>>> target_sum([1], 2)       # out of reach
0
>>> target_sum([1, 2], 0)    # +1+2, +1-2, -1+2, -1-2 give 3, -1, 1, -3
0
>>> target_sum([0, 1], 1)    # +0+1 and -0+1 are two different choices
2
>>> target_sum([2, 3], -1)   # +2-3
1
```

The five ways for the first example are `-1+1+1+1+1`, `+1-1+1+1+1`, `+1+1-1+1+1`, `+1+1+1-1+1` and `+1+1+1+1-1`.

## Constraints

- `1 <= len(nums) <= 100`, `0 <= nums[i] <= 1000`, `sum(nums) <= 10_000`, `-10_000 <= target <= 10_000`.
- A `0` counts twice: `+0` and `-0` are different choices.
- Time `O(n * sum)`. Trying all `2**n` sign patterns does not finish for `n = 100`.

## Think about

Call `P` the sum of the numbers with a `+` and `N` the sum of those with a `-`. You know `P - N` (the target) and `P + N` (the total). What is `P`? When is there no whole-number `P` at all?
