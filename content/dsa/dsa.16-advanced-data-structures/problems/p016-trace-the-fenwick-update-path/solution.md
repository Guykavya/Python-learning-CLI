## Approach

`k & -k` isolates the lowest set bit. The update adds it (carrying into a higher bit each time), the prefix query removes it (clearing one bit each time).

## Expected output

```text
update 11 : 11(1011) 12(1100) 16(10000)
update 6 : 6(110) 8(1000) 16(10000)
prefix 15 : 15(1111) 14(1110) 12(1100) 8(1000)
prefix 10 : 10(1010) 8(1000)
cells holding position 6: 3
```

## Why

| start | steps |
|---|---|
| update 11 = `1011` | `+1` → 12 = `1100`, `+4` → 16 = `10000`, `+16` → 32 > 16 |
| update 6 = `110` | `+2` → 8 = `1000`, `+8` → 16, `+16` → 32 > 16 |
| prefix 15 = `1111` | `-1` → 14, `-2` → 12, `-4` → 8, `-8` → 0 |
| prefix 10 = `1010` | `-2` → 8, `-8` → 0 |

**After you answer.**

1. Each update step makes the lowest set bit strictly higher, and 16 = `10000` is the only cell with lowbit 16, which covers everything. Starting from any `k <= 16`, the lowest bit can rise at most through 1, 2, 4, 8, 16: at most 5 cells.
2. `t[15]` covers 15, `t[14]` covers `13..14`, `t[12]` covers `9..12`, `t[8]` covers `1..8`: together exactly `1..15`, no overlap.
3. The cells that contain position 6 (6, 8, 16) are exactly the update path of 6: an update must change every cell that holds the position, and nothing else.

## Another way

Draw the bars of chapter section 10 (`fenwick_picture(16)`) and follow them by eye: an update goes to the next **longer** bar that still covers the position; a prefix query steps **left** to the bar that ends just before the current one starts.
