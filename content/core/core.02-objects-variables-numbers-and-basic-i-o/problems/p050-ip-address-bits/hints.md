## Hint 1

`192.168.1.1` is `192 * 2**24 + 168 * 2**16 + 1 * 2**8 + 1`. What does `a << 24` mean in those terms?

## Hint 2

The starter's `a << 24 + b << 16 ...` is grouped as `a << (24 + b) << ...` because `+` binds tighter
than `<<`. Bracket each shift. Since the shifted parts never overlap, `|` and `+` give the same result.

## Hint 3

To pull out an octet: shift it down to the lowest byte, then mask with `& 255` (which is `0b11111111`).
`>>` binds tighter than `&`, so `x >> 16 & 255` already means `(x >> 16) & 255`.
