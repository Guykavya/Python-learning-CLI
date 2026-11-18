# Non-overlapping intervals

A calendar has double bookings. Write `min_removals(intervals)`: return the **fewest** intervals you must delete so that no two of the remaining ones overlap.

Rules (chapter section 5):

- Each interval is a pair `(start, end)` with `start <= end`, as a tuple or a list. The list is not sorted.
- **Touching intervals do not overlap**: `(1, 2)` and `(2, 3)` can both stay.
- Return an `int`. An empty list needs `0` removals. Do not change the list you are given.

## Example

```python
>>> min_removals([(1, 2), (2, 3), (3, 4), (1, 3)])
1
>>> min_removals([(1, 2), (1, 2), (1, 2)])
2
>>> min_removals([(1, 2), (2, 3)])
0
>>> min_removals([(1, 100), (11, 22), (1, 11), (2, 12)])
2
```

In the first example removing `(1, 3)` is enough. In the last one, keeping `(1, 11)` and `(11, 22)` means removing the other two.

## Constraints

- `0 <= len(intervals) <= 10**5`. Aim for `O(n log n)`.

## Think about

Removing the fewest is the same as **keeping the most**. Which problem from section 4 keeps the most? When two intervals clash, which one should go: the one that starts later, or the one that **ends** later?
