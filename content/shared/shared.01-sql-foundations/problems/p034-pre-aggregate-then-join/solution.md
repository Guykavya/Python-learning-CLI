## Approach

Each subquery reduces its table to one row per `order_id`. Joining two one-row-per-order tables to `orders` cannot repeat anything. `LEFT JOIN` keeps orders without lines or payments, and `COALESCE` turns the resulting NULL into 0.0.

## Code

```sql
SELECT o.order_id,
       COALESCE(i.items_total, 0.0) AS items_total,
       COALESCE(p.paid, 0.0)        AS paid
FROM orders o
LEFT JOIN (SELECT order_id, SUM(qty * unit_price) AS items_total
           FROM order_items GROUP BY order_id) i ON i.order_id = o.order_id
LEFT JOIN (SELECT order_id, SUM(amount) AS paid
           FROM payments GROUP BY order_id) p ON p.order_id = o.order_id
ORDER BY o.order_id;
```

## Complexity

Each table is scanned once and grouped, then the small summaries are joined: O(lines + payments + orders). The naive double join costs O(lines x payments) per order and gives wrong sums.

## Another way / portable SQL

Two scalar subqueries in `SELECT` (`(SELECT SUM(...) FROM payments p WHERE p.order_id = o.order_id)`) also work, and `COALESCE` them. They run once per order. The pre-aggregate form with a CTE (`WITH i AS (...), p AS (...)`) is the same idea and portable to MySQL 8 and PostgreSQL.
