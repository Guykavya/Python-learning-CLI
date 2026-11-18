## Hint 1

If `len(s1) + len(s2) != len(s3)`, the answer is `False` at once. Otherwise let `f(i, j)` mean "`s3[:i + j]` is an interleaving of `s1[:i]` and `s2[:j]`". The position in `s3` is not part of the state: it is always `i + j`.

## Hint 2

The last letter `s3[i + j - 1]` came either from `s1` (then it equals `s1[i - 1]` and `f(i - 1, j)` must be True) or from `s2` (it equals `s2[j - 1]` and `f(i, j - 1)` must be True). `f(0, 0)` is True. The first row and column only have one of the two options.

## Hint 3

```
if len(s1) + len(s2) != len(s3): return False
f = (n+1) x (m+1) table of False; f[0][0] = True
for i in 0..n:
    for j in 0..m:
        if i > 0 and f[i-1][j] and s1[i-1] == s3[i+j-1]: f[i][j] = True
        if j > 0 and f[i][j-1] and s2[j-1] == s3[i+j-1]: f[i][j] = True
return f[n][m]
```
