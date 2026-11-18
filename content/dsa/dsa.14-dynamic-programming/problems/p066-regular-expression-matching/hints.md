## Hint 1

Write a tiny helper: `same(c, pc)` is True when the pattern character `pc` is `.` or equals `c`. Then, for a plain pattern character (letter or `.`): `f(i, j) = i > 0 and same(s[i-1], p[j-1]) and f(i-1, j-1)`.

## Hint 2

For `p[j-1] == '*'`, the unit is `x* = p[j-2:j]`:

- **zero** copies: skip the whole unit, `f(i, j-2)`;
- **one more** copy: `s[i-1]` must match `x` (`same(s[i-1], p[j-2])`), and then the unit stays for the letters before it: `f(i-1, j)`.

The first row matters: `""` matches `"a*b*"`, because every unit is skipped. `f(0, j) = p[j-1] == '*' and f(0, j-2)`.

## Hint 3

```
f = (n+1) x (m+1) table of False; f[0][0] = True
for j in 2..m:  if p[j-1] == '*': f[0][j] = f[0][j-2]
for i in 1..n:
    for j in 1..m:
        if p[j-1] == '*':
            f[i][j] = f[i][j-2] or (same(s[i-1], p[j-2]) and f[i-1][j])
        else:
            f[i][j] = same(s[i-1], p[j-1]) and f[i-1][j-1]
return f[n][m]
```
