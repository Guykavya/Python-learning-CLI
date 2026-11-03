## Approach

Equality columns come first, range/order columns after. `(customer_id, ordered)` serves requirements 1 and 3: all rows for one customer sit together and are already sorted by date.
`(status, ordered)` serves requirement 2. `CREATE UNIQUE INDEX` on `email` enforces requirement 4 (a unique index is how `UNIQUE` constraints are implemented).

## Code

```python
SCRIPT = """
CREATE INDEX idx_orders_cust_date   ON orders(customer_id, ordered);
CREATE INDEX idx_orders_status_date ON orders(status, ordered);
CREATE UNIQUE INDEX idx_customers_email ON customers(email);
"""
```

## Complexity

Each lookup becomes O(log n + matches) instead of O(n). Each insert now also updates up to 2 indexes on `orders` (O(log n) each). The three indexes take extra disk space proportional to the table.

## Another way / portable SQL

`CREATE UNIQUE INDEX` is the same in PostgreSQL and MySQL. Alternatively declare `email TEXT UNIQUE` in the table. PostgreSQL also offers partial indexes (`WHERE status = 'shipped'`) and `INCLUDE` columns; SQLite has partial indexes as well. Always re-check plans after you add an index: the planner decides, not you.
