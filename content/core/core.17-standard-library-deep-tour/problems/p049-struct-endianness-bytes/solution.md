## Walkthrough

1. `<I` of `0x12345678`: lowest byte first: `78 56 34 12`.
2. `>I`: highest byte first, the way we write it: `12 34 56 78`.
3. `<h` of `-2`: two's complement 16 bits is `0xFFFE`; little-endian puts `fe` first: `fe ff`.
4. `>H` of `513` = `0x0201`: `02 01`.
5. `01 00 00 00`: little-endian is `1`; big-endian is `0x01000000` = `16777216`.
6. `ff ff`: unsigned `65535`, signed `-1`.
7. `<HI` packs `7` as `07 00` and `258` (`0x102`) as `02 01 00 00`, no padding: `6 07 00 02 01 00 00`.
8. Same bytes read with `>HI`: `0x0700` = `1792`, `0x02010000` = `33619968`. Wrong byte order gives
   believable but wrong numbers: no error is raised.
9. `<BI` = 1 + 4 = `5`; `@BI` = 1 + 3 padding + 4 = `8`; `@IB` = 4 + 1 = `5` (struct never adds
   padding at the end).
10. `int.from_bytes`: big `0x0001` = `1`, little `0x0100` = `256`.
11. `3s` cuts to `b'abc'`; `5s` pads: `b'ab\x00\x00\x00'`.
12. `1.0` = `0x3F800000`: little `00 00 80 3f`, big `3f 80 00 00`.

## The exact output

```text
78 56 34 12
12 34 56 78
fe ff
02 01
1 16777216
65535 -1
6 07 00 02 01 00 00
(1792, 33619968)
5 8 5
1 256
b'abc' b'ab\x00\x00\x00'
00 00 80 3f 3f 80 00 00
```

(Line 9 is from an x86-64 / ARM64 machine; every common PC and phone gives the same, but native
sizes are exactly why file formats use `<` or `>`.)
