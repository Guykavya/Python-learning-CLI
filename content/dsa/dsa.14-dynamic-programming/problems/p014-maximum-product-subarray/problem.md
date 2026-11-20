# Maximum product subarray

Write `max_product(nums)` that returns the largest **product** of a contiguous, non-empty block of `nums`.

It looks like p013 with `*` instead of `+`, but two things change: a **negative** number turns the smallest product into the largest, and a **zero** wipes out everything before it.

## Example

```python
>>> max_product([2, 3, -2, 4])        # the block [2, 3]
6
>>> max_product([-2, 0, -1])          # the block [0]
0
>>> max_product([-2, 3, -4])          # the whole list: two negatives make a positive
24
>>> max_product([-3])
-3
```

## Constraints

- `1 <= len(nums) <= 10**5`, `-10 <= nums[i] <= 10`. Python ints never overflow, so products can be big (one test returns `2**1000`).
- `O(n)` time. Trying every block is `O(n^2)`.

## Think about

In p013 the state was "the best block ending at `i`". Is the best product ending at `i` built from the best product ending at `i - 1`? Try `[-2, 3, -4]` at `i = 2`: which block ending at index 1 do you need to extend? What extra number must the state carry?
