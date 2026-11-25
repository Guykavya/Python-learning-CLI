## Hint 1

What does `read_sql_query` accept besides the SQL text and the connection to pass values safely? What character marks the place of a value in SQLite SQL? How can the optional customer filter add a condition only when it is given?

## Hint 2

```text
sql    = "SELECT order_id, customer, order_date, qty FROM orders WHERE order_date >= ?"
params = [since]
if customer is not None:  sql += " AND customer = ?";  params.append(customer)
sql += " ORDER BY order_date, order_id"
pd.read_sql_query(sql, con, params=params, parse_dates=["order_date"])
```
