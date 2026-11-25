# Coordinates of a grid

Chapter section 2.3. For a grid (an image) with `h` rows and `w` columns, write `grid_coordinates(h, w)` that returns a
tuple `(ys, xs)` of two integer arrays, both of shape `(h, w)`:

- `ys[i, j] == i` (the row number of cell `(i, j)`),
- `xs[i, j] == j` (the column number of cell `(i, j)`).

`h` or `w` may be 0: then both arrays have that empty shape, for example `(0, 4)`. The dtype must be an integer type.
No Python loops over the cells.

## Example

```python
ys, xs = grid_coordinates(2, 3)
ys.tolist()   # [[0, 0, 0], [1, 1, 1]]
xs.tolist()   # [[0, 1, 2], [0, 1, 2]]
```

These arrays let you draw by formula later: `(ys - 5) ** 2 + (xs - 5) ** 2 < 9` is a filled circle (Ch. 20.2).
