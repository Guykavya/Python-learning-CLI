## Hint 1

First reduce: `a = a % m`. Python makes that non-negative even if `a` was negative. Then compute `gcd(a, m)`. What do
you print if it is not 1?

## Hint 2

Extended Euclid on `(a, m)` gives `a*x + m*y = g`. If `g = 1`, what is `a*x` modulo `m`? What do you do to `x` so the
answer is in `0..m-1`?

## Hint 3

```
a = a % m
g, x, y = ext(a, m)
if g != 1: print(-1)
else: print(x % m)
```
For `m = 1`: `a % 1 = 0`, `ext(0, 1)` gives `g = 1`, `x = 0`. Does the same code print 0?
