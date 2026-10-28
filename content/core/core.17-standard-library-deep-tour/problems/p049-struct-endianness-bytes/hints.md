## Hint 1

Write `0x12345678` as four bytes from the highest: `12 34 56 78`. Big-endian keeps that order;
little-endian reverses it. For `-2` in 16 bits: `-1` is `ff ff`, so `-2` is `ff fe` big-endian.
How does it look little-endian?

## Hint 2

Unpacking reads bytes as a number: `01 00 00 00` read little-endian is `0x00000001`; read big-endian
it is `0x01000000`, which is 2**24. `ff ff` is 65535 unsigned and -1 signed. For `data`: `7` is
`07 00`, `258` is `0x00000102` so `02 01 00 00`. Reading the same six bytes big-endian: the first two
bytes `07 00` are `0x0700`; the next four are `0x02010000`.

## Hint 3

Padding: `<BI` has none (1 + 4). `@BI` puts the `I` at offset 4, so 3 padding bytes follow the `B`.
`@IB`: the `I` is already at offset 0 and nothing is added after the `B`. The `s` code cuts long
bytes and pads short ones with `\x00`; a `bytes` value prints as `b'...'` with `\x00` escapes.
