## Hint 1

The base case: `b == 0`. What is `gcd(a, 0)`, and which `x` and `y` give `a*x + 0*y = a`?

## Hint 2

Suppose the recursive call `ext(b, a % b)` already gave `(g, x1, y1)` with `b*x1 + (a % b)*y1 = g`. Replace
`a % b` by `a - (a // b) * b` and collect the terms in `a` and in `b`. What are the new coefficients of `a` and `b`?

## Hint 3

```
def ext(a, b):
    if b == 0: return a, 1, 0
    g, x1, y1 = ext(b, a % b)
    return g, y1, x1 - (a // b) * y1
```
Test by hand on `ext(17, 5)`: the chain is (17,5) -> (5,2) -> (2,1) -> (1,0).
