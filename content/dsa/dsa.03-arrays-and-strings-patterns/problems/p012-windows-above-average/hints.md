## Hint 1

How many windows of size `k` are there in an array of length `n`? Write their start positions for `n = 7`, `k = 3`.

## Hint 2

Keep the current window sum `s`. Check the first window, then for each `r` from `k` to `n - 1` do
`s += a[r] - a[r - k]` and check again. "Check" means `s >= t * k`.

## Hint 3

```
need = t * k
s = sum(a[0:k]); count = 1 if s >= need else 0
for r in k .. n-1:
    s += a[r] - a[r - k]
    if s >= need: count += 1
print count
```
