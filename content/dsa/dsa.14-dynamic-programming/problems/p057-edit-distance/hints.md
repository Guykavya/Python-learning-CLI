## Hint 1

State: `f[i][j]` = the edit distance between `a[:i]` and `b[:j]`. Base cases come first: `f[i][0] = i` (delete all `i` characters) and `f[0][j] = j` (insert all `j`). These are not zeros: getting them wrong is the classic bug.

## Hint 2

If `a[i-1] == b[j-1]`, keep the character for free: `f[i][j] = f[i-1][j-1]`. Otherwise pay 1 for the cheapest of:

- replace `a[i-1]` by `b[j-1]`: `f[i-1][j-1]`
- delete `a[i-1]`: `f[i-1][j]`
- insert `b[j-1]` at the end: `f[i][j-1]`

## Hint 3

```
f = (n + 1) x (m + 1) table
f[i][0] = i for every i;  f[0][j] = j for every j
for i in 1..n:
    for j in 1..m:
        if a[i-1] == b[j-1]: f[i][j] = f[i-1][j-1]
        else: f[i][j] = 1 + min(f[i-1][j-1], f[i-1][j], f[i][j-1])
return f[n][m]
```
