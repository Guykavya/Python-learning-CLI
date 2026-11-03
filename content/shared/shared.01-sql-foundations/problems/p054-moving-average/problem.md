# Three-day moving average with ROWS BETWEEN

A *frame* limits which rows of the partition a window function sees for the current row.
`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` means: the current row and the two rows before it. Near the start there are fewer rows, and the frame simply holds what exists.

```sql
CREATE TABLE daily (day INTEGER, amount INTEGER);
INSERT INTO daily VALUES (1,10),(2,20),(3,35),(4,40),(5,50);
```

Write one `SELECT` returning `day`, `amount`, `ma3`: the average of `amount` over the current day and the two days before it (only
the days that exist), rounded to 2 decimals with `ROUND(x, 2)`. Order by `day`.

**Example**

| day | amount | ma3 |
|---|---|---|
| 1 | 10 | 10.0 |
| 2 | 20 | 15.0 |
| 3 | 35 | 21.67 |
| 4 | 40 | 31.67 |
| 5 | 50 | 41.67 |

Day 3 is (10+20+35)/3 = 21.67. Day 2 only has two days, so it is (10+20)/2 = 15.0.
