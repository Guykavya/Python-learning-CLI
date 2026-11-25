# Least squares with the normal equations

Chapter section 3.5. When `A x = b` has more equations than unknowns it usually has no exact solution. The **least-squares** solution minimises `|A x - b|^2`; it solves the **normal equations** `A^T A x = A^T b`.

Write `least_squares(A, b)` returning `x`. Use `np.linalg.solve` on the normal equations (not `lstsq`; the test turns that off). Assume `A` has full column rank.

## Example

```text
A = [[1, 0], [1, 1], [1, 2]]    b = [1, 3, 5]
least_squares(A, b)  ->  [1, 2]      (the line y = 1 + 2 x passes through all three points)
```
