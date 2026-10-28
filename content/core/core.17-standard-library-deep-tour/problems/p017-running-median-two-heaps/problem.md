# Running median with two heaps

A sensor sends one number at a time, forever. After each number you must report the **median of
everything so far**. Re-sorting the whole history on every new number costs O(n log n) per
number. Two heaps do it in O(log n):

- `low`: a **max-heap** holding the smaller half (store negated values, since `heapq` only does
  min-heaps). Its top is the biggest of the small numbers.
- `high`: a **min-heap** holding the larger half. Its top is the smallest of the big numbers.

Keep two rules true after every insert:

1. Every number in `low` is `<=` every number in `high`.
2. `len(low) == len(high)` or `len(low) == len(high) + 1`.

Then the median is the top of `low` (odd count) or the average of both tops (even count).

Write in `solution.py`:

- class `MedianKeeper` with `add(x)`, `median()` and `__len__()`.
  - `median()` with an odd count returns the middle value **itself** (an `int` stays an `int`);
    with an even count it returns `(a + b) / 2` (a `float`). This is what `statistics.median` returns.
  - `median()` on an empty keeper raises `ValueError`.
- `running_medians(nums: Iterable[float]) -> list[float]`: the median after each number, using
  `MedianKeeper`.

Use `heapq`; do not sort.

**Example**

```python
running_medians([5, 15, 1, 3])
# [5, 10.0, 5, 4.0]
#  [5] -> 5;  [5, 15] -> 10.0;  [1, 5, 15] -> 5;  [1, 3, 5, 15] -> (3 + 5) / 2 = 4.0
```
