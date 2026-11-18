# Partition equal subset sum

You have a list of positive integers. Can you split it into **two groups with equal sums**? Every number goes into exactly one group. Write `can_partition(nums)` that returns `True` or `False` (chapter section 12).

## Example

```python
>>> can_partition([1, 5, 11, 5])     # [11] and [1, 5, 5]
True
>>> can_partition([1, 2, 3, 5])      # total 11 is odd
False
>>> can_partition([3, 3, 2, 2, 2])   # [3, 3] and [2, 2, 2]
True
>>> can_partition([1, 2, 5])         # total 8, but no group sums to 4
False
>>> can_partition([7])
False
```

## Constraints

- `1 <= len(nums) <= 200`, `1 <= nums[i] <= 100`.
- Each number is used **once**. `[1, 2, 5]` is `False` even though `1 + 1 + 2 = 4`.
- Time `O(n * total)`. Trying every subset (`2**n` of them) does not finish for `n = 200`.

## Think about

If the total is `S`, what must one of the two groups sum to? Once you know that number, which problem from chapter section 12 is left? Why does a greedy "put each number in the lighter pile" not work on `[3, 3, 2, 2, 2]`?
