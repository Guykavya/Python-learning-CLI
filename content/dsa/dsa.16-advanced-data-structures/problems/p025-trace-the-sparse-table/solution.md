## Approach

Build each row from the one above (two half-blocks), then answer a query with two blocks of the largest power of two that fits.

## Expected output

```text
0 [5, 2, 4, 7, 6, 3, 1, 8]
1 [2, 2, 4, 6, 3, 1, 1]
2 [2, 2, 3, 1, 1]
3 [1]
1 7 k = 2 blocks at 1 3 -> 1
3 6 k = 1 blocks at 3 4 -> 3
2 3 k = 0 blocks at 2 2 -> 4
```

## Why

| row | entries |
|---|---|
| 0 | the array `[5, 2, 4, 7, 6, 3, 1, 8]` |
| 1 | `min` of pairs: `2, 2, 4, 6, 3, 1, 1` |
| 2 | `min(row1[i], row1[i + 2])`: `min(2,4)=2, min(2,6)=2, min(4,3)=3, min(6,1)=1, min(3,1)=1` |
| 3 | `min(row2[0], row2[4]) = min(2, 1) = 1` |

Queries: `a[1:7] = 2, 4, 7, 6, 3, 1` has minimum 1 (`min(row2[1], row2[3]) = min(2, 1)`); `a[3:6] = 7, 6, 3` has minimum 3 (`min(row1[3], row1[4]) = min(6, 3)`); `a[2:3] = 4`.

**After you answer.**

1. All three agree with `min` of the slice.
2. `(1, 7)`: blocks `[1,5)` and `[3,7)` overlap at 3 and 4. `(3, 6)`: blocks `[3,5)` and `[4,6)` overlap at 4. `(2, 3)`: both blocks are `[2,3)`, the same block twice.
3. `8 + 7 + 5 + 1 = 21` entries, against `n * log2(n) = 24`: the rows get shorter, so the table is a little below that bound.

## Another way

Answer each query from row 0 alone (scan the slice): correct, `O(r - l)` per query. The table trades `O(n log n)` memory for `O(1)` queries.
