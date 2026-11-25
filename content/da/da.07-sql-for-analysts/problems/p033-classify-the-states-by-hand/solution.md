## Approach

| user | m1 | m2 | m3 | m4 |
|---|---|---|---|---|
| 1 | new | retained | retained | retained |
| 2 | new | churned | resurrected | churned |
| 3 | | new | churned | resurrected |
| 4 | | | new | churned |

Counting each column gives the lines `1 2 0 0 0`, `2 1 1 0 1`, `3 1 1 1 1` and `4 0 1 1 2`. MAU per month is the sum of the first three counts: `[2, 2, 3, 2]`.

Identities: MAU(1) = 2 = retained(2) + churned(2) = 1 + 1; MAU(2) = 2 = 1 + 1 for month 3; MAU(3) = 3 = 1 + 2 for month 4.

## Check

Run the program and compare.

## Another way

The same table with `retained` defined as "active in `m - 1` and `m`" and `resurrected` as "active in `m`, not in `m - 1`, with an earlier month" is what `lag` over each user's active months computes: `prev = m - 1` is the one comparison that separates the two.
