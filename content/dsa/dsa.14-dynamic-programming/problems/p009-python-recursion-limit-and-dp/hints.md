## Hint 1

Recipe: state `f(i)` = the fewest moves from `i` to 1. Base `f(1) = 0`. Transition: the first move goes to `i - 1`, or `i // 2` (if even), or `i // 3` (if divisible); take `1 + min` of the allowed ones. All of them are smaller than `i`. In which direction do you fill the table?

## Hint 2

A table of size `n + 1`, filled for `i = 2, 3, ..., n`, has no recursion at all.

```
f = [0] * (n + 1)          # f[1] = 0 already
for i in 2..n:
    best = f[i - 1] + 1
    if i % 2 == 0: best = min(best, f[i // 2] + 1)
    if i % 3 == 0: best = min(best, f[i // 3] + 1)
    f[i] = best
return f[n]
```

## Hint 3

If you prefer to keep the memoised function: call it on `500, 1000, 1500, ...` up to `n` first. Each call then finds `n - 500` already in the cache and only recurses about 500 levels. That is the "warm the cache" cure; the table is simpler.
