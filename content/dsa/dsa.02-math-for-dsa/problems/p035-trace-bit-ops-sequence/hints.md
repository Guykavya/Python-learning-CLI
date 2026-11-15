## Hint 1

`45 = 0b101101`. `45 >> 2` drops the two lowest bits: `0b1011 = 11`. `45 << 3` is `45 * 8`. `45 & 15` keeps the lowest 4 bits.
`45 | 2` sets bit 1. `45 ^ 63` flips the lowest 6 bits (63 is six 1s).

## Hint 2

For `~x`, use the identity `~x = -x - 1`. For `-5 & 3`: `-5` ends in `...1011`, and `3 = 0b0011`, so `& 3` keeps the last two
bits `11`. For `|` and `^` do the same with `...11111011` and `...00000011`.

## Hint 3

`bin(-5)` prints the sign and the bin of the absolute value: `-0b101`. `x & -x` gives the lowest set bit as a number
(`40 = 0b101000` has the lowest set bit at value 8). In `5 & 5 - 1`, the `-` runs first: it is `5 & 4`.
