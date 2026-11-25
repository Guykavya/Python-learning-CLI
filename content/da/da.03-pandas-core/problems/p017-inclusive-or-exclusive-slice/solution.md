## Approach

`loc["b":"d"]` is a label slice, closed on both ends: rows `b, c, d`, shape `(3, 3)`. `iloc[1:3]` is a position slice, half-open: positions 1 and 2, rows `b, c`, shape `(2, 3)`. In `loc[:, "x":"z"]` the part before the comma is "all rows" and the part after selects the columns `x` to `z` inclusive: all three, shape `(4, 3)`. In `iloc[:, 1:]` the column positions run from 1 to the end: `y, z`, shape `(4, 2)`.

## Code

The expected output is in `expected.txt`, produced by running the program.

## Complexity

All four are slices (O(1) to create the view; Copy-on-Write copies only if you change them).

## Another way

To get rows b to d by position write `df.iloc[1:4]`: the end is one past the last row you want.
