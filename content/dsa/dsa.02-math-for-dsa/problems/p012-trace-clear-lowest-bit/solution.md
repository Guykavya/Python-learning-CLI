## Walkthrough

The loop on 44:

| n (decimal) | binary | `n & (n - 1)` |
|---|---|---|
| 44 | 101100 | 101100 & 101011 = 101000 = 40 |
| 40 | 101000 | 101000 & 100111 = 100000 = 32 |
| 32 | 100000 | 100000 & 011111 = 0 |

Three passes, so `steps 3`. The number 44 has three 1-bits.

The table lines:

| x | binary | `x & -x` | `x \| (x + 1)` | `x ^ (x - 1)` |
|---|---|---|---|---|
| 12 | 1100 | 4 | 1101 = 13 | 0111 = 7 |
| 40 | 101000 | 8 | 101001 = 41 | 001111 = 15 |
| 7 | 111 | 1 | 1111 = 15 | 001 = 1 |
| 8 | 1000 | 8 | 1001 = 9 | 0111 = 15 |

Last two lines: `5 & 3 = 1`, `5 | 3 = 7`, `5 ^ 3 = 6`; then `1 << 4 = 16`, `100 >> 3 = 12`, `6 & 1 = 0`, `7 & 1 = 1`.

Output:

```
44 101100 -> 40
40 101000 -> 32
32 100000 -> 0
steps 3
12 1100 x & -x = 4  x | (x + 1) = 13  x ^ (x - 1) = 7
40 101000 x & -x = 8  x | (x + 1) = 41  x ^ (x - 1) = 15
7 111 x & -x = 1  x | (x + 1) = 15  x ^ (x - 1) = 1
8 1000 x & -x = 8  x | (x + 1) = 9  x ^ (x - 1) = 15
1 7 6
16 12 0 1
```

## Key idea

The loop count equals the number of 1-bits (popcount). It does one pass per set bit, not one per bit position, so
it is fast for numbers with few 1-bits. `x & (x - 1) == 0` also tests whether `x > 0` is a power of two.
