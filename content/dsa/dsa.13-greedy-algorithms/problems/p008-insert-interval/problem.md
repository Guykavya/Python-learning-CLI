# Insert interval

A calendar keeps its busy periods as a **sorted** list of disjoint blocks, the output of `merge` (p007). A new booking arrives. Write `insert_interval(intervals, new)` that returns the calendar with the booking added, still sorted and disjoint.

Rules:

- `intervals` is a list of `(start, end)` pairs (tuples or lists) with `start <= end`, **sorted by start**, and no two overlap or touch (there is always a gap between one block's end and the next block's start).
- `new` is one pair `(start, end)` with `start <= end`.
- As in merge intervals, **touching intervals merge**: inserting `(5, 6)` next to `[3, 5]` gives `[3, 6]`.
- Return a **new** list of `[start, end]` lists. Do not change `intervals`.

## Example

```python
>>> insert_interval([(1, 3), (6, 9)], (2, 5))
[[1, 5], [6, 9]]
>>> insert_interval([(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], (4, 8))
[[1, 2], [3, 10], [12, 16]]
>>> insert_interval([(3, 5)], (0, 1))      # before everything
[[0, 1], [3, 5]]
>>> insert_interval([(3, 5)], (5, 6))      # touching: merges
[[3, 6]]
>>> insert_interval([], (4, 7))
[[4, 7]]
```

## Constraints

- `0 <= len(intervals) <= 10**5`. The list is already sorted, so this can be done in **one pass**, `O(n)`, without sorting again.

## Think about

The blocks fall into three groups: those that end before `new` starts, those that touch or overlap `new`, and those that start after `new` ends. What happens to each group?
