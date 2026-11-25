## Approach

The labels of `a + b` are the sorted union `a, b, c, d`. Only `b` and `c` are in both (2 + 10 and 3 + 20). `a` and `d` meet a missing side and give `nan`. `nan` is a float, so the dtype is `float64` and the numbers print as `12.0`. With `fill_value=0` the missing side counts as 0, giving `[1.0, 12.0, 23.0, 30.0]` (still float: the reindex step created the missing values first). `.values` returns the raw NumPy array, and NumPy adds by position: `[1+10, 2+20, 3+30]`.

## Code

The expected output is in `expected.txt`, produced by running the program.

## Complexity

Alignment costs O(n log n) in the worst case (building the union of labels); the position-wise sum is O(n).

## Another way

`a.reindex(total.index, fill_value=0) + b.reindex(total.index, fill_value=0)` spells out the alignment step.
