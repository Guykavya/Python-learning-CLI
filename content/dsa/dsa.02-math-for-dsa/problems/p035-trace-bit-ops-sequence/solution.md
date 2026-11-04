## Walkthrough

- `45 = 0b101101`.
  `45 >> 2 = 0b1011 = 11`; `45 << 3 = 360`; `45 & 15 = 0b1101 = 13`; `45 | 2 = 0b101111 = 47`; `45 ^ 63 = 0b010010 = 18`.
- XOR swap: `a = 12 ^ 10 = 6`; `b = 6 ^ 10 = 12`; `a = 6 ^ 12 = 10`. Result `10 12`.
- `~5 = -6`, `~0 = -1`, `~-1 = 0`.
- `-1 >> 1 = -1` (all ones stay all ones); `-8 >> 1 = -4`; `-7 >> 1 = -4` (floor of -3.5); `7 >> 1 = 3`.
- `-5 = ...11111011`. `-5 & 3 = 0b11 = 3`. `-5 | 3 = ...11111011 = -5`. `-5 ^ 3 = ...11111000 = -8`.
- `-5 & 255 = 251` (`0b11111011`). `bin(5) = '0b101'`, `bin(-5) = '-0b101'`.
- `7 & -7 = 1`, `12 & -12 = 4`, `40 & -40 = 8`: the lowest set bit.
- `1 << 10 = 1024`, `1023`, and `5 & 5 - 1 = 5 & 4 = 4`.

## Output

```
11 360 13 47 18
10 12
-6 -1 0
-1 -4 -4 3
3 -5 -8
251 0b101 -0b101
1 4 8
1024 1023 4
```

## Key ideas

- XOR swap works because `(a ^ b) ^ b = a`. It fails for `a ^= a` (a variable swapped with itself becomes 0).
- `x & -x` works in two's complement: `-x` flips all bits above the lowest set bit and keeps that bit.
- `x & (x - 1)` clears the lowest set bit. Together they are the two tools for bit tricks.
- A mask like `& 255` or `& (2**32 - 1)` is how you imitate a fixed-width integer in Python.
