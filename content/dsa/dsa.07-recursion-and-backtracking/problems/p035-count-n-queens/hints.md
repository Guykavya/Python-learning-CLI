## Hint 1

Place queens row by row: `go(r)` tries every column `c` of row `r`. Which three facts make square `(r, c)` unsafe?

## Hint 2

All squares on one `\` diagonal have the same `r - c`; on one `/` diagonal the same `r + c`. Keep `cols`, `diag`, `anti` sets; add before recursing, remove after.

## Hint 3

```
def go(r):
    if r == n: return 1
    count = 0
    for c in range(n):
        if c in cols or r - c in diag or r + c in anti: continue
        add c, r - c, r + c; count += go(r + 1); remove them
    return count
```
