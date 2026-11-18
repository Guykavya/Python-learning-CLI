## Hint 1

The coins are the squares `1, 4, 9, ...` up to `n`. `f(a)` = the fewest squares that add up to `a`. The last square is some `s <= a`, so `f(a) = 1 + min(f(a - s))`. Since 1 is a square, every `a` can be made: no `-1` case. What is `f(0)`?

## Hint 2

Build the list of squares once, before the table. Inside the loop over `a`, stop as soon as `s > a` (the list is increasing).

```
squares = [1, 4, 9, ...]   (all k*k <= n)
f = [INF] * (n + 1); f[0] = 0
for a in 1..n:
    for s in squares:
        if s > a: break
        f[a] = min(f[a], f[a - s] + 1)
return f[n]
```
