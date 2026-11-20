## Hint 1

State: `f[i][j]` = the LCS length of the prefixes `a[:i]` and `b[:j]`. Base: `f[0][j] = f[i][0] = 0` (an empty prefix has nothing in common). The table has `(len(a) + 1) x (len(b) + 1)` cells and the answer is `f[len(a)][len(b)]`.

## Hint 2

If `a[i-1] == b[j-1]`, match them: `f[i][j] = f[i-1][j-1] + 1`. Otherwise one of the two last characters is not used: `f[i][j] = max(f[i-1][j], f[i][j-1])`. Fill row by row, left to right: every cell then reads cells that are already done.

## Hint 3

```
f = (n + 1) x (m + 1) table of 0
for i in 1..n:
    for j in 1..m:
        if a[i-1] == b[j-1]: f[i][j] = f[i-1][j-1] + 1
        else:                f[i][j] = max(f[i-1][j], f[i][j-1])
return f[n][m]
```
