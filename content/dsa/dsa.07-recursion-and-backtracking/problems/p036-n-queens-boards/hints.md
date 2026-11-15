## Hint 1

Use the search from problem 35 (one queen per row, three sets), but at `r == n` record a copy of `cols_of` instead of counting.

## Hint 2

Row `r` with its queen in column `c` is `"." * c + "Q" + "." * (n - c - 1)`.

## Hint 3

```
if r == n:
    solutions.append(["." * c + "Q" + "." * (n - c - 1) for c in cols_of])
    return
```
