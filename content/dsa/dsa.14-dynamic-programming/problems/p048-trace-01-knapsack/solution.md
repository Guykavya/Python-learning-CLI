## Approach

Keep the previous line in front of you and fill the new one from right to left. The downward loop guarantees that every value you read on the right-hand side, `g[w - weight]`, comes from the previous line: that is the 2-D table's "row above", which is what makes each item usable once.

## Expected output

```text
start [0, 0, 0, 0, 0, 0, 0, 0]
item 0 (3,5) [0, 0, 0, 5, 5, 5, 5, 5]
item 1 (1,2) [0, 2, 2, 5, 7, 7, 7, 7]
item 2 (4,6) [0, 2, 2, 5, 7, 8, 8, 11]
item 3 (2,3) [0, 2, 3, 5, 7, 8, 10, 11]
best: 11
```

## Why

| item (wt, val) | changes (old value -> new value, reading the previous line) |
|---|---|
| 0 (3, 5) | `w = 3..7`: `0 + 5 = 5` beats 0 |
| 1 (1, 2) | `w = 4..7`: `g[w-1] + 2 = 5 + 2 = 7` beats 5; `w = 1, 2`: `0 + 2 = 2`; `w = 3`: `g[2] + 2 = 2` loses to 5 |
| 2 (4, 6) | `w = 7`: `g[3] + 6 = 11` beats 7; `w = 6`: `g[2] + 6 = 8`; `w = 5`: `g[1] + 6 = 8`; `w = 4`: `g[0] + 6 = 6` loses to 7 |
| 3 (2, 3) | `w = 6`: `g[4] + 3 = 10` beats 8; `w = 2`: `g[0] + 3 = 3` beats 2; `w = 7`: `g[5] + 3 = 11` ties 11; `w = 5, 3`: tie (8, 5); `w = 4`: `g[2] + 3 = 5` loses to 7 |

**After you answer.**

1. `best = 11` can be made two ways: items 0 and 2 (weights 3 + 4, values 5 + 6), or items 1, 2 and 3 (weights 1 + 4 + 2, values 2 + 6 + 3). The array only stores the value, not which items.
2. `g[4]` read `g[3]`, which was 5 from item 0. Going downwards, `w = 4` is handled **before** `w = 3`, so `g[3]` had not been changed for item 1 yet.
3. Upwards, item 0 is reused: after item 0 the array is `[0, 0, 0, 5, 5, 5, 10, 10]` (`g[6] = g[3] + 5` reads the cell just set). At the end every capacity is filled with copies of item 1 (weight 1, value 2) and `best` is **14**: seven copies of an item that exists once.

## Another way

Fill the 2-D table `f[i][w]` of chapter section 10 for the same items: one row per item. Its rows are exactly the lines above. The 1-D array is that table with only the last row kept.
