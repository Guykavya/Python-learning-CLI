# Path with minimum effort

`heights` is a grid of numbers (a list of rows). You walk from the top-left cell `(0, 0)` to the bottom-right cell, moving **up, down, left or right** (no diagonals). The **effort** of a route is the **largest** absolute height difference between two consecutive cells on it. Write `minimum_effort(heights)`: the smallest effort of any route.

The cost of a route is not a sum but a **maximum**. Dijkstra still works if you change one line: the "distance" of a cell is the best effort of a route to it, and walking from `u` to a neighbour `v` gives `max(effort[u], |h[u] - h[v]|)`.

## Example

```python
>>> minimum_effort([[1, 2, 2],
...                 [3, 8, 2],
...                 [5, 3, 5]])
2
```

The route `1 -> 3 -> 5 -> 3 -> 5` (down the left column, then along the bottom row) has differences `2, 2, 2, 2`: effort 2. The route along the top row, `1 -> 2 -> 2 -> 2 -> 5`, has a step of 3.

## Constraints

- `1 <= rows, cols <= 100`, `1 <= heights[r][c] <= 10**6`. A 1x1 grid has effort 0.
- Do not change `heights`.

## Think about

Why is "max" still safe for Dijkstra (what property of `+` with non-negative weights did the proof need, and does `max` have it)? Why is BFS on the number of steps the wrong tool?
