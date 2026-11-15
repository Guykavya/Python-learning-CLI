# Shortest path in a grid with BFS

A maze is a list of equal-length strings: `.` is a free cell, `#` is a wall. From a cell you can move one step **up, down, left or right** to a free cell inside the grid. Write `shortest_path(grid, start, goal)` that returns the fewest steps from `start` to `goal` (both `(row, col)` tuples), or `-1` if the goal cannot be reached.

- If `start == goal` (and it is free), the answer is `0`.
- If `start` or `goal` is a wall, the answer is `-1`.

Use **breadth-first search** with a `collections.deque` as the queue (chapter section 12, "BFS on a grid"). Import it as `from collections import deque`.

**Mark a cell as seen when you put it into the queue, not when you take it out.** Otherwise a cell can be enqueued several times by different neighbours before it is processed. The answer stays correct, but the work grows; one test counts how many times your queue's `append` is called on an open 30 x 30 grid and fails if it is more than the number of cells.

## Example

```python
>>> maze = ["..#....",
...         ".##.##.",
...         "....#..",
...         ".##...#",
...         "...#..."]
>>> shortest_path(maze, (0, 0), (4, 6))
10
>>> shortest_path(maze, (0, 0), (0, 3))
7
>>> shortest_path(["..#.", "..#.", "..#."], (0, 0), (0, 3))
-1
```

## Constraints

- `1 <= rows, cols <= 300`.

## Think about

Why does the **first** time BFS reaches the goal give the shortest distance? Would a stack (DFS) give the same guarantee?
