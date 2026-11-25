## Hint 1

Which function turns a Parquet file into a table inside a query? Which two columns does the question really need, and how do you write the June condition so that both boundary instants are right (one is in, one is out)?

## Hint 2

```text
SELECT COALESCE(sum(amount), 0)
FROM read_parquet('<path>')
WHERE order_time >= TIMESTAMP '2025-06-01' AND order_time < TIMESTAMP '2025-07-01'
```

`sum` of no rows is `NULL`: wrap it so that an empty month gives 0. Fetch with `con.execute(...).fetchall()[0][0]` (not `fetchone`).
