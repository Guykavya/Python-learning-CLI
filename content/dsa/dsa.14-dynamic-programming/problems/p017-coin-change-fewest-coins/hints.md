## Hint 1

`f(a)` = the fewest coins that make exactly `a`. The last coin is some `c <= a`, and the rest is `a - c`, which needs `f(a - c)` coins. Which `c` should you pick? What is `f(0)`?

## Hint 2

Unreachable amounts must lose every `min`, so give them a value bigger than any real answer: `float("inf")` (and `inf + 1` is still `inf`). Convert to `-1` only when you return.

## Hint 3

```
INF = float("inf")
f = [INF] * (amount + 1); f[0] = 0
for a in 1..amount:
    for c in coins:
        if c <= a and f[a - c] + 1 < f[a]:
            f[a] = f[a - c] + 1
return f[amount] if f[amount] != INF else -1
```
