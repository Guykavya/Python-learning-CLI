# Merge intervals

A log lists the times when a server was busy, in any order and with overlaps. Write `merge(intervals)` that returns the busy periods as a list of **disjoint** intervals.

Rules (chapter section 6):

- Each interval is a pair `(start, end)` with `start <= end`, as a tuple or a list. The list is not sorted.
- **Touching intervals merge**: `(1, 3)` and `(3, 5)` become `[1, 5]`.
- Return a **new** list of `[start, end]` lists, sorted by start, with no two overlapping or touching. An empty input gives `[]`.
- Do not change the list you are given.

## Example

```python
>>> merge([(1, 3), (2, 6), (8, 10), (15, 18)])
[[1, 6], [8, 10], [15, 18]]
>>> merge([(1, 4), (4, 5)])
[[1, 5]]
>>> merge([(1, 10), (2, 3), (4, 5)])
[[1, 10]]
>>> merge([(8, 10), (1, 3)])
[[1, 3], [8, 10]]
```

## Constraints

- `0 <= len(intervals) <= 10**5`. Aim for `O(n log n)`.

## Think about

In the third example, `(2, 3)` lies inside `(1, 10)`. What goes wrong if you set the end of the current block to `3` instead of keeping `10`?
