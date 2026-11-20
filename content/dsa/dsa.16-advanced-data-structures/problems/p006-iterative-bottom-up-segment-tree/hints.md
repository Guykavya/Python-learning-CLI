## Hint 1

Start with `l += n` and `r += n` (the half-open leaf range). While `l < r`: if `l` is odd, it is a right child whose parent also covers an element left of the range, so take `t[l]` and move `l` one step right. If `r` is odd, `r - 1` is a left child inside the range: step `r` back and take `t[r]`. Then go up: `l //= 2`, `r //= 2`.

## Hint 2

Nodes taken on the left side come **before** everything taken later on the left; nodes taken on the right come **after** everything taken later on the right. So keep `resl = combine(resl, t[l])` and `resr = combine(t[r], resr)`, and return `combine(resl, resr)`.

## Hint 3

```
update(i, v): i += n; t[i] = v; while i > 1: i //= 2; t[i] = f(t[2i], t[2i+1])
query(l, r):
    resl = resr = identity; l += n; r += n
    while l < r:
        if l % 2 == 1: resl = f(resl, t[l]); l += 1
        if r % 2 == 1: r -= 1; resr = f(t[r], resr)
        l //= 2; r //= 2
    return f(resl, resr)
```
