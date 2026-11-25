## Hint 1

Build `A = [1 | X]` first. Then the loop is the same as in problem 33 with the gradient of problem 29.

## Hint 2

```text
A = column_stack([ones(n), X]); w = zeros(d + 1)
repeat steps times: w = w - lr * 2 / n * A.T @ (A @ w - y)
```
