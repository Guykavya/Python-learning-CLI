## Hint 1

`f(i)` = the number of ways to stand on step `i`. The last move into step `i` was a 1-step (from `i - 1`) or a 2-step (from `i - 2`). Those two groups do not overlap and cover every way. So what is `f(i)`? What are `f(0)` and `f(1)`?

## Hint 2

The modulo is safe to apply at every step: `(x + y) % M` is the same as `((x % M) + (y % M)) % M`. So store every table cell already reduced.

## Hint 3

```
M = 10**9 + 7
f = [0] * (n + 1)
f[0] = 1
if n >= 1: f[1] = 1
for i in 2..n:
    f[i] = (f[i-1] + f[i-2]) % M
return f[n]
```
