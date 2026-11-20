## Hint 1

`pre[k]` is the sum of the first `k` elements, so the sum of `a[l:r]` is `pre[r] - pre[l]`: the first `r` elements minus the first `l`.

## Hint 2

`a[i]` is inside every prefix that is longer than `i`: `pre[i + 1]` to `pre[n]`. Changing `a[i]` by `delta = v - a[i]` changes each of them by `delta`. Keep a copy of `a` so you know the old value.

## Hint 3

```
set(i, v):
    delta = v - a[i]; a[i] = v
    for k in range(i + 1, n + 1): pre[k] += delta
    return n - i
```
