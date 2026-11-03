# Month-over-month change with LAG

`LAG(col)` returns the value of `col` from the *previous* row in the window's order. For the first row there is no previous row, so the
result is `NULL` (you may pass a default as a third argument). `LEAD` is the same but looks forward.

```sql
CREATE TABLE monthly_sales (month TEXT, revenue INTEGER);
INSERT INTO monthly_sales VALUES ('2024-01',100),('2024-02',120),('2024-03',90),('2024-04',90);
```

Write one `SELECT` returning `month`, `revenue`, `change`, where `change` is this month's revenue minus the previous month's.
For the first month `change` must be `NULL`. Order by `month`.

**Example**

| month | revenue | change |
|---|---|---|
| 2024-01 | 100 | NULL |
| 2024-02 | 120 | 20 |
| 2024-03 | 90 | -30 |
| 2024-04 | 90 | 0 |
