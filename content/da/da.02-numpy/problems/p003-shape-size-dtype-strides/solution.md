## Approach

Work out the shape first, then the strides from the rule of Ch. 3.3, then adjust for the operation:

- `a` is `(2, 3)`: a row is 3 × 8 = 24 bytes, so strides `(24, 8)`.
- `t = a.T` swaps the axes: shape `(3, 2)` and strides `(8, 24)`. Nothing is copied; only the recipe changed.
- `c` is `(2, 3, 4)`: strides `(3·4·8, 4·8, 8) = (96, 32, 8)`, 24 elements, 3 axes.
- `s = a[:, ::2]` keeps both rows and columns 0 and 2: shape `(2, 2)`, size 4. Moving down a row still jumps 24 bytes; moving one step right now skips a column, so 16 bytes.

The last two lines show the values: `s` is `[[0, 2], [3, 5]]` and `t` is `[[0, 3], [1, 4], [2, 5]]`.

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

All four arrays share at most one block: `t` and `s` are views of `a` (strides you cannot get from the C rule are the sign of a view).

## Another way

Check yourself in a REPL with `x.flags["C_CONTIGUOUS"]`: it is `True` for `a` and `c` and `False` for `t` and `s`.
