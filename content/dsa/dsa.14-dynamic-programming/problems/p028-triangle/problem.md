# Triangle

`triangle` is a list of rows; row `i` has `i + 1` numbers. Start at the top. From position `j` in one row you may move to position `j` or `j + 1` in the next row. Write `min_triangle_path(triangle)` that returns the smallest possible sum of a path from the top to the **bottom row** (any position in it).

## Example

```python
>>> min_triangle_path([[2],
...                    [3, 4],
...                    [6, 5, 7],
...                    [4, 1, 8, 3]])        # 2 + 3 + 5 + 1
11
>>> min_triangle_path([[-10]])
-10
>>> min_triangle_path([[1], [2, 3]])
3
```

## Constraints

- `1 <= len(triangle) <= 400`, values are integers in `-1000 .. 1000` (they may be negative).
- Solve it **bottom-up**: start from the last row and move up. Then the answer ends in one cell (the top), and you need `O(n)` extra memory for one row.

## Think about

1. Top-down, `f[i][j]` = the cheapest path from the top to `(i, j)`. Where can you come from? Which cells on the edges have only one parent? Where is the answer?
2. Now flip it: `g[i][j]` = the cheapest path from `(i, j)` **down to the bottom**. What is `g` on the bottom row? What is `g[i][j]` in terms of the row below? Where is the answer now, and why are there no edge cases?
