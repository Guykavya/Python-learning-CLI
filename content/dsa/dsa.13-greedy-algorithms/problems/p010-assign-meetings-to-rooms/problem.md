# Assign meetings to rooms

Chapter section 6 counts the rooms a set of meetings needs. An office manager needs more: **which** room each meeting goes in. Write `assign_rooms(meetings)` that returns a list `rooms` where `rooms[i]` is the room number of `meetings[i]` (input order), using the **fewest rooms possible**.

Rules:

- Each meeting is a pair `(start, end)` of integers with `start < end`, as a tuple or a list. The list is not sorted.
- Rooms are numbered `0, 1, 2, ...` with no gaps: if you use `k` rooms, the numbers used are exactly `0 .. k-1`.
- Two meetings in the same room must not overlap. Meetings are half-open, and the chapter's rule applies: **a meeting that ends at time `t` frees its room for a meeting that starts at `t`**.
- The number of rooms must be the minimum, which is the **largest number of meetings running at one moment** (chapter section 6, "interval partitioning").
- Any valid assignment with the fewest rooms is accepted. An empty list gives `[]`. Do not change the list you are given.

## Example

```python
>>> assign_rooms([(0, 30), (5, 10), (15, 20)])
[0, 1, 1]
>>> assign_rooms([(1, 5), (2, 6), (3, 7), (4, 8)])
[0, 1, 2, 3]
>>> assign_rooms([(3, 5), (1, 3), (5, 7)])          # touching: one room is enough
[0, 0, 0]
```

In the first example `(5, 10)` and `(15, 20)` can share room 1, because the first ends at 10, before 15. `[1, 0, 0]` would also be accepted.

## Constraints

- `0 <= len(meetings) <= 10**5`. Aim for `O(n log n)`: a min-heap (`heapq`) of the rooms in use.

## Think about

The chapter's `min_rooms` keeps a heap of **end times** only. What else must each heap entry carry so that you know **which** room becomes free?
