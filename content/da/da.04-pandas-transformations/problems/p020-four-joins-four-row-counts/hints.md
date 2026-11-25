## Hint 1

Make a small table of the keys: for each customer id, how many rows does it have in `cust`, and how many in `orde`?
A matched key gives (left count × right count) rows. An unmatched key gives one row, if its side is kept.

## Hint 2

```text
key  cust  orde   matched?
C1   1     2      yes -> 2 rows
C2   1     0      left only
C3   1     1      yes -> 1 row
C4   1     0      left only
C5   1     0      left only
C9   0     1      right only
inner = matched rows; left = matched + left only; right = matched + right only; outer = all
a left-only row has NaN in the order columns: integers cannot hold NaN
```
