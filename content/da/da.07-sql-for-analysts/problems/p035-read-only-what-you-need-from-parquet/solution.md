## Approach

Query the file in place. Only `amount` and `order_time` appear in the query, so the engine can skip the other columns in the file; the date filter uses a half-open interval (`>=` start, `<` next start) so that every instant belongs to exactly one month.

## Code

```python
def june_revenue(con, path):
    sql = f"""
        SELECT COALESCE(sum(amount), 0)
        FROM read_parquet('{path}')
        WHERE order_time >= TIMESTAMP '2025-06-01' AND order_time < TIMESTAMP '2025-07-01'
    """
    return con.execute(sql).fetchall()[0][0]
```

## Complexity

One scan of two columns of the file. With pushdown, row groups outside the date range may be skipped.

## Another way

Load the whole file with `pd.read_parquet(path)` and filter in pandas: it reads *every* column (including `note`) into memory first. `pd.read_parquet(path, columns=["order_time", "amount"])` gets the same saving by hand. `EXPLAIN` shows what DuckDB plans to read: the scan lists the projected columns and the pushed-down filter (Ch. 9.3).

## Pitfall to remember

`BETWEEN '2025-06-01' AND '2025-06-30'` loses the last day after midnight. Use a half-open interval for time ranges.
