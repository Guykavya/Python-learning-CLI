## Hint 1

Write the gradient in the form `X^T (p - y) / n` where `p = sigmoid(z)`. Which part can overflow, and for which sign of `z`?

## Hint 2

```text
e = exp(-abs(z))                 # never larger than 1
p = where(z >= 0, 1 / (1 + e), e / (1 + e))
return X.T @ (p - y) / n
```
