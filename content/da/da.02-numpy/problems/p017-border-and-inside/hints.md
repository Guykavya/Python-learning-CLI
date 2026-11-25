## Hint 1

Write the four pieces separately for a 3 × 4 array: which slice is the top row? The right column *without* its top cell? The bottom row backwards *without* its right cell? The left column upwards *without* both corners? Then: what goes wrong with these slices when there is only one row or one column?

## Hint 2

```text
if h == 1: return the row
if w == 1: return the column
top    = a[0, :]
right  = a[1:, -1]
bottom = a[-1, -2::-1]      # from the second-to-last column back to column 0
left   = a[-2:0:-1, 0]      # from the second-to-last row up to row 1
return np.concatenate([top, right, bottom, left])
interior = a[1:-1, 1:-1]
```
