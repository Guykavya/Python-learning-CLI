## Hint 1

Two choices for the letter `s[i-1]`: skip it, which leaves `f(i-1, j)` ways; or match it with `t[j-1]`, which is only possible when the letters are equal, and leaves `f(i-1, j-1)` ways. The two choices give different position sets, so the counts **add**.

## Hint 2

Base cases: `f(i, 0) = 1` for every `i` (the empty `t` is picked in exactly one way: pick nothing), and `f(0, j) = 0` for `j > 0` (an empty `s` cannot give a non-empty `t`). Table size `(len(s) + 1) x (len(t) + 1)`; the answer is the corner.

## Hint 3

```
f = table of zeros, (n+1) x (m+1)
for i in 0..n: f[i][0] = 1
for i in 1..n:
    for j in 1..m:
        f[i][j] = f[i-1][j]
        if s[i-1] == t[j-1]:
            f[i][j] += f[i-1][j-1]
return f[n][m]
```
