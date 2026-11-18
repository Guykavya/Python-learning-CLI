## Approach

Fill the table row by row. Equal letters copy the diagonal; different letters take `1 +` the smallest of the three neighbours (replace = diagonal, delete = up, insert = left). Row 0 and column 0 are the base cases.

## Expected output

```text
- 0 1 2 3 4 5 6 7
k 1 1 2 3 4 5 6 7
i 2 2 1 2 3 4 5 6
t 3 3 2 1 2 3 4 5
t 4 4 3 2 1 2 3 4
e 5 5 4 3 2 2 3 4
n 6 6 5 4 3 3 2 3
distance: 3
```

## Why

The columns are `"" s i t t i n g`. The cells that copy their diagonal (equal letters) are:

| cell | letters | copies |
|---|---|---|
| `f[2][2]` | i = i | `f[1][1] = 1` |
| `f[2][5]` | i = i | `f[1][4] = 4` |
| `f[3][3]` | t = t | `f[2][2] = 1` |
| `f[3][4]` | t = t | `f[2][3] = 2` |
| `f[4][3]` | t = t | `f[3][2] = 2` |
| `f[4][4]` | t = t | `f[3][3] = 1` |
| `f[6][6]` | n = n | `f[5][5] = 2` |

Every other cell is `1 + min(up-left, up, left)`. Two cells as examples: `f[5][5]` (`e` against `i`) is `1 + min(f[4][4] = 1, f[4][5] = 2, f[5][4] = 2) = 2`; the corner `f[6][7]` (`n` against `g`) is `1 + min(f[5][6] = 3, f[5][7] = 4, f[6][6] = 2) = 3`.

The path back from the corner: `f[6][7]` came from the left (`f[6][6] = 2`): **insert g**. `f[6][6]` is a match (n). `f[5][5]` came from the diagonal `f[4][4] = 1`: **replace e by i**. Then matches t, t, i down to `f[1][1] = 1`, which came from `f[0][0]`: **replace k by s**. Three operations, as in the chapter: replace k by s, replace e by i, insert g.

Neighbouring cells differ by at most 1, because one extra letter costs at most one extra operation. So a `1` next to a `3` is always an arithmetic slip.

## Another way

Fill the table column by column instead (outer loop over `j`). Every cell still has its three neighbours ready, so the numbers are the same; only the printing order in the program fixes the layout. Doing it both ways on paper is a good self-check.
