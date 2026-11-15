# Rotting oranges (multi-source BFS)

A grid (a list of lists) holds `0` (empty), `1` (a fresh orange) and `2` (a rotten orange). Every minute, each fresh orange that is next to a rotten one (up, down, left, right) becomes rotten. Write `minutes_to_rot(grid)` that returns the number of minutes until **no fresh orange is left**, or `-1` if some fresh orange can never rot.

- No fresh orange at the start: `0` minutes (even if there are no rotten ones).
- An empty grid `[]`: `0`.
- You may change `grid` (the tests pass a copy).

All rotten oranges spread **at the same time**. Put all of them into the queue at the start and run BFS **one level per minute** (chapter section 12, "Multi-source BFS").

## Example

```python
>>> minutes_to_rot([[2, 1, 1], [1, 1, 0], [0, 1, 1]])
4
>>> minutes_to_rot([[2, 1, 1], [0, 1, 1], [1, 0, 1]])
-1
>>> minutes_to_rot([[0, 2]])
0
>>> minutes_to_rot([[2, 1, 1, 1, 2]])
2
```

In the last example the two rotten oranges work from both ends and meet in the middle after 2 minutes. Starting a separate BFS from each rotten orange would give 3 for the middle one.

## How it is tested

Fixed cases and 500 random grids compared with a minute-by-minute simulation; one grid of 200 x 200.

## Constraints

- `0 <= rows, cols <= 200`.

## Think about

How do you know where one minute ends and the next begins in the queue? What has to be true when the loop stops for the answer to be `-1`?
