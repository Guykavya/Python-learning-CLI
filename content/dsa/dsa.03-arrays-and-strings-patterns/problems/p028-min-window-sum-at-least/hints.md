## Hint 1

Grow a window `a[l..r]` by moving `r` to the right. Once its sum reaches `s`, the window is good. Can a good window
get shorter and stay good? Which end would you cut?

## Hint 2

While the sum is still `>= s`, record the length `r - l + 1`, then drop `a[l]` and move `l` right. It must be a
`while`, not an `if`: one new big element can allow several cuts. Start the best length at a value no window can
have (such as `n + 1`) and turn it into `0` at the end if nothing was found.

## Hint 3

```
best = n + 1; total = 0; l = 0
for r in 0..n-1:
    total += a[r]
    while total >= s:
        best = min(best, r - l + 1)
        total -= a[l]; l += 1
print best if best <= n else 0
```
