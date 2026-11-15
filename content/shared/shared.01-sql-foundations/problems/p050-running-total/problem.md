# Running total per store

A *running total* (cumulative sum) shows, for each row, the sum of everything up to and including that row.
`SUM(amount) OVER (ORDER BY day)` does this. Add `PARTITION BY store` and the total restarts for each store.

```sql
CREATE TABLE daily_sales (day TEXT, store TEXT, amount REAL);
INSERT INTO daily_sales VALUES
 ('2024-01-01','A',10),('2024-01-02','A',20),('2024-01-03','A',5),
 ('2024-01-01','B',7),('2024-01-03','B',3);
```

Write one `SELECT` returning `store`, `day`, `amount`, `running`, where `running` is the sum of `amount` for that store from its
first day up to this day. Order the result by `store`, then `day`. In this exercise a store has at most one row per day.

**Example**

| store | day | amount | running |
|---|---|---|---|
| A | 2024-01-01 | 10 | 10 |
| A | 2024-01-02 | 20 | 30 |
| A | 2024-01-03 | 5 | 35 |
| B | 2024-01-01 | 7 | 7 |
| B | 2024-01-03 | 3 | 10 |
