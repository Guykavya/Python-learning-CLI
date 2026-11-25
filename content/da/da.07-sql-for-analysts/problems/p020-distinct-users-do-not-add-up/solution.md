## Approach

| day | rows | distinct users |
|---|---|---|
| 1 | (1, 2, 3) | 3 |
| 2 | (2, 2, 3, 4) | 3 (user 2 twice) |
| 3 | (1, 3, 3) | 2 (user 3 twice) |

- Line 1: `[3, 3, 2]`.
- Line 2: the sum is `8`.
- Line 3: users 1, 2, 3, 4 → `4`.
- Line 4: ten rows → `10`.
- Last line: days 2 and 3 have counts 3 and 2, a sum of `5`; the distinct users over the two days are 2, 3, 4 and 1: `4`. The line prints `5 4`.

## Check

Run the program and compare.

## Another way

For a true weekly count, `count(DISTINCT user_id)` over the whole week (Ch. 5.2). To see how much the daily numbers overlap, compute `sum(daily) / distinct` (here 2.0): the average number of days a user was active.
