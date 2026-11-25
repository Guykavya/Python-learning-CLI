# Matrix product three ways

Chapter section 2.2. The entry `C[i][j]` of the product `C = A B` is the dot product of **row i of A** with **column j of B**. The shapes must fit: `(m x n)(n x p) -> (m x p)`.

Write `matmul(A, B)` using loops (three nested loops or a loop with a dot product) and return a NumPy array. If the inner sizes do not match, raise `ValueError` with a message that contains both shapes. Do not use `@`, `np.dot` or `np.matmul` for the whole product (the test only checks the result and the error).

## Example

```text
A = [[1, 2], [3, 4]]      B = [[0, 1], [1, 0]]
matmul(A, B)  ->  [[2, 1], [4, 3]]
```
