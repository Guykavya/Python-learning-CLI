## Hint 1

Base cases. `f(0, 0)` is True (empty matches empty). `f(i, 0)` is False for `i > 0` (an empty pattern matches nothing else). And the first row: `f(0, j)` is True only while `p[:j]` is all stars. What is `f(0, 2)` for the pattern `"*a"`?

## Hint 2

For `p[j-1] == '*'`: `f(i, j) = f(i, j-1)` (the star is empty) **or** `f(i-1, j)` (the star eats `s[i-1]` and is still available, so `j` does not move). Moving to `f(i-1, j-1)` would let a star eat at most one letter.

For a letter or `?`: `f(i, j) = f(i-1, j-1)` when `p[j-1] == '?'` or `p[j-1] == s[i-1]`, else False.

## Hint 3

```
f = (n+1) x (m+1) table of False; f[0][0] = True
for j in 1..m: f[0][j] = f[0][j-1] and p[j-1] == '*'
for i in 1..n:
    for j in 1..m:
        if p[j-1] == '*':  f[i][j] = f[i][j-1] or f[i-1][j]
        elif p[j-1] == '?' or p[j-1] == s[i-1]:  f[i][j] = f[i-1][j-1]
return f[n][m]
```
