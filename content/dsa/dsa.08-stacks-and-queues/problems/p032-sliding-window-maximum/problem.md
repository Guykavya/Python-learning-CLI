# Sliding window maximum

A window of width `k` slides over `nums` one step at a time. Write `window_max(nums, k)` that returns the maximum of every window, from left to right. There are `len(nums) - k + 1` windows; if `k > len(nums)` there are none and you return `[]`.

Calling `max` on every window costs `O(n * k)`. Use the **monotonic deque** of chapter section 11 instead: a deque of indices whose values decrease from front to back, so the front is always the maximum of the current window. The whole scan must be `O(n)`: the last test has `n = 200,000` and `k = 100,000` with a time limit.

## Example

```python
>>> window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
[3, 3, 5, 5, 6, 7]
>>> window_max([9, 3, 2, 1], 2)
[9, 3, 2]
>>> window_max([4, 2], 1)
[4, 2]
>>> window_max([4, 2], 3)
[]
```

## Constraints

- `1 <= k`, `0 <= len(nums) <= 2 * 10**5`.

## Think about

Why may an index leave the deque from the **back** (it was beaten by a newer, larger value) and also from the **front** (it got too old)? Can the same index leave twice?
