# Scaling speeds descent

Chapter section 8.5. How fast gradient descent converges depends on the **shape** of the loss bowl: if one feature has a much larger scale than another, the bowl is a long narrow valley and descent zig-zags. Standardising makes the bowl round.

Write `steps_to_converge(X, y, lr, tol, max_steps=100_000)`: run gradient descent on the mean squared error (no intercept; start from zeros; gradient `(2/n) X^T (X w - y)`) and return the **number of steps** after which the gradient norm is below `tol`. If it never gets there, return `max_steps`.

## Example

```text
X = standardised data, lr = 0.5, tol = 1e-6   ->  a few dozen steps
the same data with one column multiplied by 20 (and a learning rate that is stable for it) -> thousands of steps
```
