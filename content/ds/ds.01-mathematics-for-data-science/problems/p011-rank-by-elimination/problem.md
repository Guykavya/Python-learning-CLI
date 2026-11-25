# Rank by elimination

Chapter section 3.4. The **rank** of a matrix is the number of independent rows (equal to the number of independent columns). In elimination it is the number of columns that still have a usable pivot.

Write `rank(A)` for any `m x n` matrix (not only square ones), using row operations with partial pivoting and a tolerance of `1e-10` times the largest absolute entry of `A`. Do not call `np.linalg.matrix_rank` or `np.linalg.svd` (the test turns them off).

## Example

```text
rank([[1, 2], [2, 4]])               ->  1
rank([[1, 0, 0], [0, 1, 0]])         ->  2
rank([[0, 0], [0, 0]])               ->  0
```
