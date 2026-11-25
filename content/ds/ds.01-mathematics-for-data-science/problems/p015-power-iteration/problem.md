# Power iteration

Chapter section 4.3. If you multiply a vector again and again by a symmetric matrix `A` and rescale it to length 1, it turns towards the eigenvector with the **largest** eigenvalue. The eigenvalue itself is `v^T A v` (the Rayleigh quotient).

Write `power_iteration(A, steps=500, seed=0)` returning `(value, vector)`: start from a random vector made with `np.random.default_rng(seed)`, repeat `steps` times `v = A v / |A v|`, and return the Rayleigh quotient and the unit vector. The matrix is symmetric with a clearly largest positive eigenvalue.

## Example

```text
A = [[2, 1], [1, 2]]
power_iteration(A)  ->  (3.0, [0.7071, 0.7071])      (the sign of the vector may differ)
```
