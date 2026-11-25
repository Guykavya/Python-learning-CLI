## Hint 1

For a fresh (C-contiguous) array, the last axis has stride `itemsize` (8 here), and each earlier axis jumps over a whole sub-block: `itemsize` times the product of all the later lengths. What does `.T` do to the shape and to the strides?

## Hint 2

```text
a: shape (2, 3)    strides (3*8, 8)
t: shape reversed  strides reversed (no data moves)
c: shape (2, 3, 4) strides (3*4*8, 4*8, 8)
s: a[:, ::2] keeps 2 rows, takes columns 0 and 2
   rows still 24 bytes apart, columns now 2*8 bytes apart
```
`size` is the product of the shape; `ndim` is its length.
