# Detect a singular system

Chapter section 3.3. If the rows of `A` are not independent (one is a combination of the others), `A x = b` has no unique solution: the matrix is **singular**. In elimination this shows up as a pivot that is (almost) zero, even after choosing the largest candidate.

Extend your `solve(A, b)` from the previous problem: after choosing the pivot for a column, if its absolute value is below `1e-12` times the largest absolute entry of `A`, raise `ValueError` with a message that contains the word `singular`. A non-singular system must still be solved. Still no `np.linalg.solve`, `inv` or `lstsq`.

## Example

```text
solve([[1, 2], [2, 4]], [1, 2])   ->  ValueError: singular matrix ...
solve([[1, 2], [3, 4]], [5, 6])   ->  [-4, 4.5]
```
Row 2 of the first matrix is twice row 1, so no unique answer exists.
