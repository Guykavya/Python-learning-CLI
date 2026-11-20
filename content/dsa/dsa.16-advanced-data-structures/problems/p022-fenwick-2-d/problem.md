# Fenwick 2-D

A warehouse floor is a grid of `rows x cols` shelves. Pallets are added to and removed from single shelves, and the manager asks how many pallets stand in a rectangle of shelves. Write `Fenwick2D` (chapter section 14). Rectangles are **half-open and 0-indexed**: rows `[r1, r2)`, columns `[c1, c2)`.

- `Fenwick2D(rows, cols)`: an empty grid;
- `add(r, c, v)`: add `v` to the shelf `(r, c)`;
- `rect(r1, c1, r2, c2)`: the total of the rectangle (0 if it is empty).

## Example

```python
>>> f = Fenwick2D(3, 4)
>>> grid = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
>>> for r in range(3):
...     for c in range(4):
...         f.add(r, c, grid[r][c])
>>> f.rect(0, 0, 3, 4), f.rect(1, 1, 3, 3), f.rect(0, 0, 1, 4), f.rect(2, 2, 2, 4)
(78, 34, 10, 0)
>>> f.add(1, 2, 100)
>>> f.rect(1, 1, 3, 3), f.rect(1, 2, 2, 3)
(134, 107)
```

## Constraints

- Grids up to 300 x 300 and 10**5 operations, each `O(log rows * log cols)`. Adding up the rectangle is `O(rows * cols)` per question.

## Think about

1. Which cells `t[i][j]` contain the shelf `(r, c)`? (Two nested lowbit loops.)
2. How do four prefix rectangles `[0, r) x [0, c)` give any rectangle? Which signs?
3. What happens when `r1 == r2` or `c1 == c2`?
