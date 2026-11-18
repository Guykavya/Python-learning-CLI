# Maximum subarray (Kadane)

Write `max_subarray(nums)` that returns the largest sum of a **contiguous, non-empty** block of `nums` (chapter section 5).

## Example

```python
>>> max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])     # the block [4, -1, 2, 1]
6
>>> max_subarray([-3, -1, -2])                         # all negative: the least bad single item
-1
>>> max_subarray([5, -9, 6])
6
```

## Constraints

- `1 <= len(nums) <= 10**5`, `-1000 <= nums[i] <= 1000`.
- The block must contain at least one item, so the answer can be negative.
- `O(n)`. Trying every block is `O(n^2)`: 5 billion blocks for `n = 10**5`.

## Think about

Chapter section 5 warns that the state "best sum among the first `i` items" has no clear transition. Which **stronger** state does it use instead, and where is the final answer then?
