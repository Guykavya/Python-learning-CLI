## Hint 1

If you laid the rows end to end, which index would the number at row `r`, column `c` have? And how do you go back from an index to `(r, c)`?

## Hint 2

Index `i` lives at row `i // C`, column `i % C`. Run the classic closed search over `i` in `[0, R*C - 1]` and read the value with `m[i // C][i % C]`.

## Hint 3

```
lo, hi = 0, R * C - 1
while lo <= hi:
    mid = (lo + hi) // 2
    v = m[mid // C][mid % C]
    if v == x: print(mid // C, mid % C); break
    elif v < x: lo = mid + 1
    else: hi = mid - 1
else: print(-1, -1)
```
