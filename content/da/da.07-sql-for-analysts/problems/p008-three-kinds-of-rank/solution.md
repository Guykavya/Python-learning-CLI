## Approach

Sort, then number. After sorting by amount descending the order is 2, 3, 6, 1, 4, 5 (orders 2 and 3 tie at 500).

| order | amount | rn | rk | dr | half |
|---|---|---|---|---|---|
| 2 | 500 | 1 | 1 | 1 | 1 |
| 3 | 500 | 2 | 1 | 1 | 1 |
| 6 | 400 | 3 | 3 | 2 | 1 |
| 1 | 300 | 4 | 4 | 3 | 2 |
| 4 | 200 | 5 | 5 | 4 | 2 |
| 5 | 100 | 6 | 6 | 5 | 2 |

`rank` gives the two tied rows rank 1 and then **skips** to 3 (two rows share rank 1, so the next row is the third). `dense_rank` gives 2 to the next row. The last line prints the largest `rk` (6) and the largest `dr` (5).

## Check

Run the program and compare.

## Another way

For "the top 3 distinct amounts" use `dense_rank() <= 3`; for "exactly 3 rows" use `row_number() <= 3` with a tie-break; for "the rows whose position is at most 3, ties included" use `rank() <= 3`.
