## Hint 1

Write the five rows with their days in a table on paper. For `rows_sum`, only positions count. For `range_sum`, look at the **day value** of every row and decide which rows have a day between (day - 1) and day. For `default_sum`, start at the top and stop after the current day (all rows of the same day included).

## Hint 2

```text
rows_sum   : id1 = 10 ; id2 = 10+20 ; id3 = 20+30 ; id4 = 30+40 ; id5 = 40+50
range_sum  : id1 days 0-1 ; id2,id3 days 1-2 (all three rows) ; id4 days 2-3 ; id5 days 4-5 (only itself)
default_sum: running total up to and including the last peer of the current day
```
