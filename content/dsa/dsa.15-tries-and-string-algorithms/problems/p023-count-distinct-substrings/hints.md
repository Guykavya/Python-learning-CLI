## Hint 1

When `c` is appended to `t` (giving `u = t + c`, length `L`), the only possible new substrings are the suffixes of `u`. A suffix that already occurred somewhere earlier in `u` is not new, and if a suffix occurred earlier, so did every shorter suffix. So if the longest earlier-occurring suffix has length `k`, exactly `L - k` new substrings appear.

## Hint 2

Reverse `u`: its suffixes become prefixes of `v = reversed(u)`. "The suffix of length `k` occurs earlier in `u`" means "the prefix of length `k` of `v` occurs again at some position `j >= 1` of `v`". The Z-function measures exactly that: `k = max(z[1:])` of `v` (0 if `L == 1`).

## Hint 3

```
total = 0
for L in 1..n:
    v = s[:L][::-1]
    z = z_function(v)
    total += L - max(z[1:], default=0)
return total
```

`O(n)` per step, `O(n**2)` in total, and only `O(n)` memory at a time.
