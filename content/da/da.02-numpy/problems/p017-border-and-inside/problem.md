# Border and inside

Chapter sections 7.2, 7.6 and 5.5. For a 2-D array `a` (a small image or a game board) write:

- `border_values(a)`: a 1-D array with the values on the border, **clockwise from the top-left corner**: the top row
  left to right, the right column downwards, the bottom row right to left, the left column upwards. Every cell
  appears **once** (corners are not repeated).
- `interior(a)`: the array without its outer ring, `a` with the first and last row and column removed. It is a view.

Edge cases: a 1 × 1 array's border is its one value; a 1 × n array's border is the row left to right; an n × 1
array's border is the column top to bottom. The interior of an array with fewer than 3 rows or columns is empty, with
shape `(max(h − 2, 0), max(w − 2, 0))`.

Use slices (a negative step reverses), no loops over the cells.

## Example

```python
a = np.arange(12).reshape(3, 4)
# [[ 0  1  2  3]
#  [ 4  5  6  7]
#  [ 8  9 10 11]]
border_values(a).tolist()   # [0, 1, 2, 3, 7, 11, 10, 9, 8, 4]
interior(a).tolist()        # [[5, 6]]
```
