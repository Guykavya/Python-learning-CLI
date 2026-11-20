## Hint 1

Write the letters of `"sitting"` above the columns and of `"kitten"` down the side **before** you fill anything. Most mistakes in this trace are comparing the wrong pair of letters. Column 1 is `s`, column 7 is `g`; row 1 is `k`, row 6 is `n`.

## Hint 2

Row `k` is easy: `k` matches nothing in `"sitting"`, so every cell is `1 + min(...)`, and you get `1 1 2 3 4 5 6 7`. Row `i` has two matches (columns 2 and 5, both `i`): those cells copy the diagonal from row `k`, which gives `1` and `4`.

## Hint 3

The two `t` rows match columns 3 and 4. In the first `t` row, `f[3][3]` copies `f[2][2] = 1`; in the second, `f[4][4]` copies `f[3][3] = 1`. Row `e` has no match; row `n` matches column 6 and copies `f[5][5]`. The last cell is `1 + min(f[5][6], f[5][7], f[6][6])`.
