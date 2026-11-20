# Unique paths with obstacles

`grid` is a list of rows; `0` is an open cell and `1` is an obstacle. Moving only **right** or **down**, count the paths from the top-left cell to the bottom-right cell that never step on an obstacle. Write `paths_with_obstacles(grid)` (chapter section 8). Return just the number.

## Example

```python
>>> paths_with_obstacles([[0, 0, 0],
...                       [0, 1, 0],
...                       [0, 0, 0]])
2
>>> paths_with_obstacles([[0, 1],
...                       [0, 0]])
1
>>> paths_with_obstacles([[1, 0]])       # the start is blocked
0
>>> paths_with_obstacles([[0]])
1
```

## Constraints

- `1 <= rows, cols <= 200`. The start and the end cell may be obstacles too: then the answer is 0.
- A recursion without a memo is exponential; a 200 by 200 grid must finish in well under a second.

## Think about

1. What is `f` of a blocked cell, and why does that one rule also stop every path that would pass through it?
2. In the grid without obstacles the first row was all 1s. Is that still true if there is an obstacle in the first row? What about the cells to its right?
3. Where does the "1" that starts all the counting come from, and what must happen when the start itself is blocked?
