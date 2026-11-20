## Hint 1

In the 2-D version, "take item `i`" is `f[i-1][w - wt] + val`: the row **above**, built from items before `i` only. That is what guarantees "at most once". The 1-D array keeps one row and overwrites it in place, so the question is only: when you read `g[w - wt]`, is it still the old row's value, or the new row's?

## Hint 2

Draw `g` for `W = 7` and the single item (2, 10). Run the upward loop by hand: `w = 2` sets `g[2] = g[0] + 10 = 10`. Then `w = 4` reads `g[2]`, which you **just** changed... Continue to `w = 6`. Now run the downward loop: `w = 7` first, then 6, 5, ..., and every read is of a cell still equal to 0.
