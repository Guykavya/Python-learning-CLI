# Read only what you need from Parquet

Chapter sections 9.2 and 9.3. Parquet is a **columnar** file: a query that needs two columns can read just those two, and a filter
on a column can discard rows while reading. DuckDB queries the file directly: `SELECT ... FROM read_parquet('file.parquet')`. The
habit to build: **name the columns you need**, filter in SQL, and never `SELECT *` from a big file.

Write

```python
def june_revenue(con, path):
    ...
```

`con` is an open DuckDB connection and `path` is the path (a string) of a Parquet file with the columns
`order_id, user_id, order_time, plan, amount, note` (`note` is a wide text column you do **not** need). Return the **total `amount` of the
orders placed in June 2025** (from `2025-06-01 00:00:00` up to but not including `2025-07-01 00:00:00`) as a number, `0` when
there is none. The query must name its columns: it must not contain `SELECT *`, and it must read the file with `read_parquet`.

```python
import duckdb, pandas as pd
orders = pd.DataFrame({
    "order_id": [1, 2, 3, 4, 5],
    "user_id": [1, 2, 3, 1, 4],
    "order_time": pd.to_datetime(["2025-05-31 23:59:59", "2025-06-01 00:00:00", "2025-06-15 12:00:00",
                                  "2025-06-30 23:59:59", "2025-07-01 00:00:00"]),
    "plan": ["monthly", "annual", "monthly", "monthly", "annual"],
    "amount": [499, 3999, 499, 499, 3999],
    "note": ["x" * 20] * 5})
orders.to_parquet("orders.parquet", index=False)
con = duckdb.connect()
# from solution import june_revenue
print(june_revenue(con, "orders.parquet"))        # 4997 for the data above
```

## Example

The data above has five orders. The ones at `2025-05-31 23:59:59` and `2025-07-01 00:00:00` are **outside** June; the three in
June add up to 3999 + 499 + 499 = 4997.
