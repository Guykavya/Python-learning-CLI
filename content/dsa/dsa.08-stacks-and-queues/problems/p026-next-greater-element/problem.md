# Next greater element

Write `next_greater(nums)` that returns a list `ans` of the same length: `ans[i]` is the first number to the **right** of position `i` that is **strictly greater** than `nums[i]`, or `-1` if there is none.

Use a monotonic stack of indices (chapter section 9): scan left to right; a new number `x` is the answer for every waiting index whose value is smaller than `x`; then `x` itself starts waiting.

## Example

```python
>>> next_greater([2, 1, 2, 4, 3])
[4, 2, 4, -1, -1]
>>> next_greater([2, 2, 3])
[3, 3, -1]
>>> next_greater([5, 4, 3])
[-1, -1, -1]
>>> next_greater([])
[]
```

In `[2, 2, 3]` the first `2` is not "greater" than the second `2`, so its answer is `3`.

## How it is tested

Fixed cases, then 1,000 random lists compared with the slow double loop, and a list of 100,000 numbers that must finish within a time limit (the double loop needs about 5 * 10**9 steps for it).

## Constraints

- `0 <= len(nums) <= 10**5`; the numbers can be negative. The answer `-1` is used even if `-1` appears in `nums`.

## Think about

Why is the stack never "increasing" from bottom to top? What would an increasing pair mean?
