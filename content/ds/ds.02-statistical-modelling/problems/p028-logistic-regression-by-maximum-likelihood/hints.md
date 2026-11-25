## Hint 1

What is the shape of `X.T @ (y - p)`? What does each Newton step do if the model is already at the maximum?

## Hint 2

```text
b = zeros(p)
repeat up to 50 times:
    p = sigmoid(X @ b)
    grad = X.T @ (y - p)
    H = X.T @ (X * (p * (1 - p))[:, None])
    step = solve(H, grad)
    b = b + step
    stop when max |step| < 1e-10
```
