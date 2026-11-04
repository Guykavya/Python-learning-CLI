## Hint 1

Write 44 in binary: `101100`. What is `44 - 1` in binary? Which bits changed compared with 44?

## Hint 2

`101100 & 101011 = 101000`. Do the same for 40 (`101000`) and 32 (`100000`). The loop ends when `n` becomes 0.
Each pass clears one 1-bit.

## Hint 3

For `x & -x`: `-x` is `~x + 1`. For 12 (`1100`), the lowest set bit has value 4, so `12 & -12 = 4`.
For `x | (x + 1)` with 12: `1100 | 1101 = 1101 = 13`. For `x ^ (x - 1)`: all bits from the lowest 1 downward
are set; for 12 that is `111 = 7`.
