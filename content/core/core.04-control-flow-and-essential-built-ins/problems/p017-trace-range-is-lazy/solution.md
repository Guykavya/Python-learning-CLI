## Walkthrough

`r` is 3, 7, 11, 15, 19, 23, 27 (31 would pass 30).

| Line | Output | Why |
|---|---|---|
| `print(r)` | `range(3, 30, 4)` | a range prints as its call, not its numbers |
| `len, r[0], r[-1], r[2]` | `7 3 27 11` | seven numbers; 3 + 2 * 4 = 11 |
| `in` tests | `True False False` | 15 - 3 = 12 is a multiple of 4; 16 is not; 31 is past the stop |
| `r[1:4]` | `range(7, 19, 4)` | items 7, 11, 15 as a range ending before 19 |
| `list(r[1:4])` | `[7, 11, 15]` | |
| `range(0, 10, 3)[-1]` | `9` | 0, 3, 6, 9 |
| `len(big)` | `200000000000` | 10**12 / 5, worked out instantly |
| `big[10**11]` | `500000000000` | 0 + 10**11 * 5 |
| `999_999_999_995 in big` | `True` | below the stop, divisible by 5 |
| `reversed(range(1, 8, 3))` | `[7, 4, 1]` | 1, 4, 7 backwards |
| empty range | `0 False True` | `range(10, 0)` is empty and falsy; `range(1)` has one number |
| equality | `True` | both are 0, 2, 4 |

None of this needs memory for the numbers. Creating `big` and asking about it is instant.
