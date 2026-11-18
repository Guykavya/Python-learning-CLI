# Minimum score triangulation

A convex polygon has `n` corners, numbered `0` to `n - 1` in order around it, and corner `i` carries the number `values[i]`. Cut the polygon into `n - 2` triangles with straight lines between corners (a **triangulation**: the lines do not cross). A triangle with corners `x, y, z` scores `values[x] * values[y] * values[z]`; the score of the triangulation is the sum over its triangles.

Write `min_score_triangulation(values)` that returns the **smallest** possible score.

## Example

```python
>>> min_score_triangulation([1, 2, 3])          # already a triangle
6
>>> min_score_triangulation([3, 7, 4, 5])       # cut 0-2: 3*7*4 + 3*4*5 = 84 + 60
144
>>> min_score_triangulation([1, 3, 1, 4, 1, 5])
13
```

For the square `[3, 7, 4, 5]` there are two triangulations: the cut `0-2` scores `144`, the cut `1-3` scores `7*4*5 + 3*7*5 = 140 + 105 = 245`.

## Constraints

- `3 <= len(values) <= 150`, `1 <= values[i] <= 100`.
- `O(n^3)` time. The number of triangulations grows like `4^n`.

## Think about

Look at the side between corner `i` and corner `j` of the polygon piece made of corners `i, i+1, ..., j`. In any triangulation of that piece, this side belongs to **exactly one** triangle. Its third corner is some `k` between them. What is left on each side of that triangle? Compare with matrix chain multiplication (p069): which part of the formula changes?
