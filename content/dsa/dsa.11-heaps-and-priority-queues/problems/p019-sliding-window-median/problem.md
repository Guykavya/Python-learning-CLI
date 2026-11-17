# Sliding window median

Write `sliding_median(nums, k)`. A window of `k` consecutive numbers slides over `nums` from left to right, one step at a time. Return the median of every window, as a list with `len(nums) - k + 1` items:

- `k` odd: the middle number of the sorted window (an item of `nums`, so an `int` stays an `int`);
- `k` even: the average of the two middle numbers, `(a + b) / 2`.

If `nums` is empty, or `k < 1`, or `k > len(nums)`, return `[]`. Do not change `nums`.

## Example

```python
>>> sliding_median([1, 3, -1, -3, 5, 3, 6, 7], 3)
[1, -1, -1, 3, 5, 6]
>>> sliding_median([1, 2, 3, 4, 2, 3, 1, 4, 2], 2)
[1.5, 2.5, 3.5, 3.0, 2.5, 2.0, 2.5, 3.0]
>>> sliding_median([5], 1)
[5]
```

The windows of the first example are `[1, 3, -1]`, `[3, -1, -3]`, `[-1, -3, 5]`, `[-3, 5, 3]`, `[5, 3, 6]`, `[3, 6, 7]`, with medians `1, -1, -1, 3, 5, 6`.

## Constraints

- Up to 100,000 numbers, windows up to 20,000 numbers, values may repeat and may be negative.
- The big test (100,000 numbers, `k = 20000`) runs in a separate process with a 10-second limit. Sorting every window takes several minutes, and so does deleting the leaving number from a heap with `list.remove` (`O(k)` per step).
- Take the idea of section 8 (two heaps) together with section 11 (lazy deletion). The chapter shows the two pieces separately; this problem joins them.

## Think about

When the window moves, one number leaves and one number enters. Which half does the leaving number sit in? You cannot remove an item from the middle of a `heapq` heap cheaply. What do you do instead, and how do you count the *live* numbers of each half? Two equal numbers can sit in different halves: how do you tell which of them is leaving?
