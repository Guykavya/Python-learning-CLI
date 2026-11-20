# Activity selection

A hall can host one event at a time. Write `max_activities(intervals)`: given a list of requests `(start, end)`, return the **largest number** of requests that can all be held, with no two overlapping.

Rules (the same as chapter section 4):

- Each request is a pair `(start, end)` with `start <= end`, given as a tuple or a list. The list is **not sorted**.
- Events are **half-open** `[start, end)`: an event that ends at 5 and one that starts at 5 do **not** overlap. Touching is fine.
- Return only the count, an `int`. The empty list gives `0`.
- Do not change the list you are given.

Use the greedy rule that the chapter proves: **earliest finish first**.

## Example

```python
>>> max_activities([(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)])
4
>>> max_activities([(0, 3), (3, 6), (6, 9)])     # touching: all three fit
3
>>> max_activities([(0, 10), (1, 2), (3, 4), (5, 6)])
3
>>> max_activities([])
0
```

In the first example the chosen events are `(1, 4), (5, 7), (8, 11), (12, 16)`. In the last-but-one, the long event `(0, 10)` starts first but blocks three short ones.

## Constraints

- `0 <= len(intervals) <= 10**5`; times are integers. Aim for `O(n log n)`.

## Think about

Why must the comparison be `start >= last_end` and not `start > last_end`? Which example above would change?
