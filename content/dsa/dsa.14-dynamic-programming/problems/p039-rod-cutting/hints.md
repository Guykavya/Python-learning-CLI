## Hint 1

Let `f[m]` be the best money for a rod of length `m`. The first piece has some length `k` from 1 to `m` (`k = m` means "no cut"). It sells for `price[k - 1]`, and the rest is a rod of length `m - k`, worth at best `f[m - k]`.

## Hint 2

So `f[m] = max(price[k - 1] + f[m - k] for k in 1..m)`, with `f[0] = 0`. Fill `f` for `m = 1, 2, ..., n` in that order, because `f[m]` reads only shorter rods.

## Hint 3

```
f = [0] * (n + 1)
for m in 1..n:
    for k in 1..m:
        f[m] = max(f[m], price[k - 1] + f[m - k])
return f[n]
```
