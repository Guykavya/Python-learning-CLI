# Gaussian elimination

Chapter section 3.2. To solve `A x = b`, turn `A` into an upper-triangular matrix with **row operations** (forward elimination), then solve upwards (back substitution). **Partial pivoting** swaps in the row with the largest entry in the current column, so you never divide by a zero (or a tiny number) on the diagonal.

Write `solve(A, b)` returning `x` as a 1-D float array. Do not call `np.linalg.solve`, `inv` or `lstsq` (the test turns them off). Do not change the inputs `A` and `b`.

## Example

```text
solve([[2, 1], [1, 3]], [3, 5])   ->  [0.8, 1.4]
solve([[0, 1], [1, 0]], [4, 7])   ->  [7, 4]     (zero on the diagonal: you must swap rows)
```
