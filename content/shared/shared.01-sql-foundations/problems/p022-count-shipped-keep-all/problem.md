# Keep all customers, count only shipped orders

Same idea as the trace in p021, now as a report. You need **every** customer, even those with zero shipped orders, and a
count of their **shipped** orders. This mixes a LEFT JOIN (keep everyone), a condition (shipped only) and `COUNT` with `GROUP BY` (one row per customer).

`COUNT(col)` counts the rows where `col` is **not NULL**; `COUNT(*)` counts rows, whatever they hold.

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE orders (
  order_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  status      TEXT NOT NULL      -- 'shipped', 'pending' or 'cancelled'
);
INSERT INTO customers VALUES (1, 'Asha'), (2, 'Ben'), (3, 'Chen'), (4, 'Dia'), (5, 'Eli');
INSERT INTO orders VALUES (20, 1, 'shipped'), (21, 1, 'shipped'), (22, 1, 'pending'),
                          (23, 2, 'pending'), (24, 3, 'shipped'), (25, 5, 'cancelled');
```

Return `name` and `shipped_orders` for every customer. Row order does not matter. Put the SQL in `QUERY`.

**Example.** Asha has three orders but only two shipped, so her count is 2. Dia has none, so her count is 0 (not missing).
