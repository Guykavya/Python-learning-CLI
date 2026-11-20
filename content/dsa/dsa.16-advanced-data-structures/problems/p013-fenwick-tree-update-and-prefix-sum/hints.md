## Hint 1

`k & -k` is the lowest set bit of `k`. Cell `t[k]` covers the positions `k - lowbit(k) + 1 .. k` (1-indexed). A prefix `1..r` is tiled by `t[r]`, then `t[r - lowbit(r)]`, and so on down to 0: **drop the lowest bit** each step.

## Hint 2

The cells that contain position `k` are `t[k]`, `t[k + lowbit(k)]`, ... while `<= n`: **add the lowest bit** each step. Convert the user's 0-indexed `i` to `k = i + 1` first; with `k = 0` the loop never moves.

## Hint 3

```
add(i, v):  k = i + 1; while k <= n: t[k] += v; k += k & -k
prefix(r):  total = 0; while r > 0: total += t[r]; r -= r & -r; return total
```

Note that `prefix(r)` needs no shift: "the first `r` elements" in 0-indexing ends at 1-indexed position `r`.
