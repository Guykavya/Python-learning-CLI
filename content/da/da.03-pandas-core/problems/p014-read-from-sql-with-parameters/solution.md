## Approach

Build the SQL text from fixed pieces only (the `?` markers and column names you wrote yourself) and keep every **value** in a separate `params` list. The database driver then treats the values as data, so a quote or a piece of SQL inside a value cannot change the query. Filtering and sorting happen in the database, which is what it is good at; `parse_dates` converts the text dates into datetimes on the way in.

## Code

```python
import pandas as pd


def orders_since(con, since, customer=None):
    sql = "SELECT order_id, customer, order_date, qty FROM orders WHERE order_date >= ?"
    params = [since]
    if customer is not None:
        sql += " AND customer = ?"
        params.append(customer)
    sql += " ORDER BY order_date, order_id"
    return pd.read_sql_query(sql, con, params=params, parse_dates=["order_date"])
```

## Complexity

The database scans or uses an index; pandas only receives the rows that matched.

## Another way

Read everything with `SELECT *` and filter in pandas: fine for a small table, wasteful for a big one, and the database cannot use its indexes. Never do `f"... WHERE customer = '{customer}'"`.
