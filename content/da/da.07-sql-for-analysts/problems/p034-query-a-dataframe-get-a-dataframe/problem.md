# Query a DataFrame, get a DataFrame

Chapter section 9.1. DuckDB and pandas work together: you give a DataFrame to a connection with `con.register("name", df)`, you
query it by that name with SQL, and `.df()` returns the answer as a DataFrame. In programs, prefer `register` to relying on a
Python variable of the same name (a typo in a variable name becomes a confusing error).

Two measured facts of DuckDB 2.0 to respect: a relation has **no `fetchone()`**, and `con.execute(...).fetchone()` leaves an
unfinished result, so the **next** query on the same connection fails with `ResourceInUseException`. Use `.df()` or `.fetchall()`.

Write the function

```python
def revenue_by_plan(con, orders):
    ...
```

It receives an open DuckDB connection `con` and a DataFrame `orders` (columns `order_id, user_id, order_time, plan, amount`). It must
register `orders` on the connection under the name `orders`, run **one** SQL query, and return the result as a pandas DataFrame
with the columns:

| column | meaning |
|---|---|
| `plan` | the plan |
| `orders` | the number of orders of the plan |
| `revenue` | the sum of `amount` of the plan |

sorted by `revenue` from largest to smallest, ties by `plan` (A to Z). The connection must still be usable afterwards, and
a second call with a **different** DataFrame must see the new data. Do not open your own connection.

```python
import duckdb, pandas as pd
orders = pd.DataFrame({
    "order_id": [9001, 9002, 9003, 9004, 9005, 9006],
    "user_id": [1, 2, 3, 1, 2, 4],
    "order_time": pd.to_datetime(["2025-05-01", "2025-05-03", "2025-05-04", "2025-06-01", "2025-06-02", "2025-06-03"]),
    "plan": ["monthly", "annual", "monthly", "monthly", "annual", "quarterly"],
    "amount": [499, 3999, 499, 499, 3999, 1299]})
con = duckdb.connect()
# from solution import revenue_by_plan
print(revenue_by_plan(con, orders))
```

## Example

On the data above the result has three rows: `annual` (2 orders, 7998), `monthly` (3 orders, 1497) and `quarterly` (1 order, 1299),
in that order.
