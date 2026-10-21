# Count the islands

A map is a list of strings of equal length; `#` is land and `.` is water. An **island** is a group
of land cells connected up, down, left or right (not diagonally).

Write:

1. `island_sizes(grid)` that returns a list of the sizes of all islands, **largest first**.
2. `count_islands(grid)` that returns how many islands there are (use `island_sizes`).

Use a **recursive** flood fill: from a land cell, visit its four neighbours, and theirs, marking
cells as visited. Keep the visited cells in a set of `(row, col)` tuples or in your own copy of the
grid; the caller's `grid` must not change.

**Example**

```python
grid = ["##..#",
        "#...#",
        "..#..",
        "....#"]
island_sizes(grid)    # [3, 2, 1, 1]
count_islands(grid)   # 4
count_islands([])     # 0
```
