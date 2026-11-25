## Hint 1

Where do you check the gradient norm: before the update or after it? Decide so that a start that already satisfies the tolerance returns 0.

## Hint 2

```text
w = zeros(d)
for step in range(max_steps):
    g = gradient(w)
    if |g| < tol: return step
    w = w - lr * g
return max_steps
```
