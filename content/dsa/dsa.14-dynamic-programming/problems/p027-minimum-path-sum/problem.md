# Minimum path sum

Each cell of `grid` holds a cost (an integer `>= 0`). Moving only **right** or **down**, go from the top-left cell to the bottom-right cell. The cost of a path is the sum of **all** the cells it visits, both ends included. Write `min_path_sum(grid)` that returns the smallest possible cost (chapter section 8).

## Example

```python
>>> min_path_sum([[1, 3, 1],
...               [1, 5, 1],
...               [4, 2, 1]])          # 1 -> 3 -> 1 -> 1 -> 1
7
>>> min_path_sum([[1, 2, 3]])          # one row: no choice
6
>>> min_path_sum([[5]])
5
```

## Constraints

- `1 <= rows, cols <= 200`, `0 <= grid[r][c] <= 100`.
- A recursion without a memo is exponential.

## Think about

1. `f[r][c]` = the cheapest cost of a path from `(0, 0)` to `(r, c)`, **including** the cost of `(r, c)`. What is `f[0][0]`?
2. Cells in the first row have no cell above. What is their formula?
3. Why is it safe to fill the table row by row, left to right?
