## Approach

| id | day | amount | rows_sum | range_sum | default_sum |
|---|---|---|---|---|---|
| 1 | 1 | 10 | 10 | 10 | 10 |
| 2 | 2 | 20 | 30 | 60 | 60 |
| 3 | 2 | 30 | 50 | 60 | 60 |
| 4 | 3 | 40 | 70 | 90 | 100 |
| 5 | 5 | 50 | 90 | 50 | 150 |

- `rows_sum` is the sum of the previous row and the current row, whatever their days are (id 5 adds id 4 although day 4 does not exist).
- `range_sum` takes all rows whose day is within 1 of the current day: ids 2 and 3 are peers (same day) and both see days 1 and 2 (10+20+30 = 60); id 4 (day 3) sees days 2 and 3 (20+30+40 = 90); id 5 (day 5) sees days 4 and 5, but day 4 does not exist, so only itself.
- `default_sum` is the running total including all peers: ids 2 and 3 both show 60, not 30 and 60.

## Check

Run the program and compare.

## Another way

To get "the last 7 days" reliably, build a **complete calendar** (Ch. 5.1) so that one row is one day, then `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` is exactly seven days. With gaps in the data, use `RANGE BETWEEN INTERVAL 6 DAYS PRECEDING AND CURRENT ROW` on a date column.
