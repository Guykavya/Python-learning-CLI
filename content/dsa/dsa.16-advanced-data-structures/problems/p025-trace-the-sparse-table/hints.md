## Hint 1

Row 1 (blocks of 2) is the minimum of each neighbouring pair: `min(5, 2), min(2, 4), min(4, 7), ...` (7 entries).

## Hint 2

Row 2 (blocks of 4) uses row 1 entries 2 apart: `min(row1[0], row1[2])`, `min(row1[1], row1[3])`, ... (5 entries). Row 3 has one entry: `min(row2[0], row2[4])`.

## Hint 3

`(1, 7)`: length 6, `k = 2`, blocks at 1 and `7 - 4 = 3`. `(3, 6)`: length 3, `k = 1`, blocks at 3 and `6 - 2 = 4`. `(2, 3)`: length 1, `k = 0`, both blocks at 2.
