# Minimum path with the path itself

As in minimum path sum: each cell of `grid` has a cost `>= 0`, you move only **right or down** from the top-left to the bottom-right, and a path costs the sum of all its cells. Now return the path too. Write `min_path(grid)` that returns a tuple `(total, route)`:

- `total` is the smallest cost;
- `route` is a list of `(row, col)` cells from `(0, 0)` to `(rows - 1, cols - 1)`, each step one cell right or down, whose cells add up to `total`.

## Example

```python
>>> min_path([[1, 3, 1],
...           [1, 5, 1],
...           [4, 2, 1]])
(7, [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)])
>>> min_path([[5]])
(5, [(0, 0)])
```

When several paths have the same smallest cost, **any one of them** is accepted. The tests check that your route is legal and that its cells add up to the minimum; they do not compare it with one fixed list.

## Constraints

- `1 <= rows, cols <= 200`, `0 <= grid[r][c] <= 100`.
- Keep the whole table (section 9 explains why reconstruction needs it).

## Think about

1. After the table `f` is full, stand on the bottom-right cell. Which neighbour did the best path come from? How can you tell from `f` alone?
2. When you walk back, you collect the cells from the end to the start. What must you do before returning them?
3. On the first row, which way must you step back?
