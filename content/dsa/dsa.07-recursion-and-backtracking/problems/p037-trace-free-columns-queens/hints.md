## Hint 1

`diag` holds `r - c` for the three queens: `0 - 1`, `1 - 3`, `2 - 5`. `anti` holds `r + c`: `0 + 1`, `1 + 3`, `2 + 5`. `sorted` prints them in increasing order.

## Hint 2

Row 3: the free columns are those not in `{1, 3, 5}`, i.e. 0, 2, 4. Check `3 - c` and `3 + c` for each of them.

## Hint 3

After placing in row 3 at the **last** free column, add that column, `3 - c` and `3 + c` to the sets before testing row 4.
