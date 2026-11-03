# Conditional aggregation: CASE and FILTER

You often need several counts in **one** row: how many orders in total, how many shipped, how many cancelled. Instead of
three queries, put the condition *inside* the aggregate.

```sql
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, ordered TEXT, status TEXT);
INSERT INTO orders VALUES
 (101,1,'2024-01-05','shipped'),(102,1,'2024-02-10','shipped'),(103,4,'2024-02-11','cancelled'),
 (104,2,'2024-03-01','shipped'),(105,3,'2024-03-15','shipped');
```

Return one row per customer (customers that appear in `orders`), ordered by `customer_id`:

| column | meaning |
|---|---|
| `customer_id` | the customer |
| `total` | all orders of the customer |
| `shipped` | orders with status `'shipped'` |
| `cancelled` | orders with status `'cancelled'` |

Write it **twice**:

- `QUERY_A` with `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`;
- `QUERY_B` with the `FILTER (WHERE ...)` clause: `COUNT(*) FILTER (WHERE status = 'shipped')`.

Both must give the same rows. (`FILTER` works in SQLite 3.30+ and PostgreSQL; MySQL does not have it, so MySQL users use the `CASE` form.)

**Example.** Customer 4 has one order and it is cancelled, so the row is `(4, 1, 0, 1)`.
