## Hint 1

Output line `j` is column `j` of the input. Which cells of the input are in column `j`?

## Hint 2

Build a new grid `t` with `c` rows and `r` columns. For every `i` in `range(r)` and `j` in `range(c)`, set
`t[j][i] = g[i][j]`. Create each row of `t` separately: `[[0] * r for _ in range(c)]`, not `[[0] * r] * c`.

## Hint 3

```
read g (r rows)
for j in range(c):
    row = [g[i][j] for i in range(r)]
    print row
```
