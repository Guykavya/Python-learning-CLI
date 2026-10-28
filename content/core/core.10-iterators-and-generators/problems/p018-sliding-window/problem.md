# Sliding window over a stream

A weather station sends one temperature each hour. To smooth the data, you want the
**moving average** of the last `k` readings. The first step is a sliding window.

Write a **generator function** `windows(iterable, k)` in `solution.py`. It yields tuples of
`k` items that sit next to each other. Each new window moves one step to the right.
If the input has fewer than `k` items, it yields nothing. You can assume `k >= 1`.

Rules that the tests check:

1. It is a generator and works on an **endless** input.
2. To give the first window it reads **only `k`** items.

**Example**

```python
list(windows([1, 2, 3, 4, 5], 3))   # [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
list(windows("abc", 2))             # [('a', 'b'), ('b', 'c')]
list(windows([1, 2], 3))            # []

temps = [20, 22, 21, 25, 30]
[sum(w) / len(w) for w in windows(temps, 2)]   # [21.0, 21.5, 23.0, 27.5]
```
