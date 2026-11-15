## Approach

Layer 1 turns lines into orders. Layer 2 turns orders into customers (counting orders in `order_totals`, where each order is one row, so no fan-out). The last query joins names and compares each customer's average to the average over all orders (a scalar subquery on layer 1).

## Code

```sql
WITH order_totals AS (
    SELECT o.order_id, o.customer_id, SUM(oi.qty * oi.unit_price) AS total
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id, o.customer_id
),
customer_stats AS (
    SELECT customer_id, COUNT(*) AS n_orders, SUM(total) AS spent
    FROM order_totals
    GROUP BY customer_id
)
SELECT c.name, s.n_orders, s.spent,
       ROUND(s.spent * 1.0 / s.n_orders, 2) AS avg_order
FROM customer_stats s
JOIN customers c ON c.customer_id = s.customer_id
WHERE s.spent * 1.0 / s.n_orders > (SELECT AVG(total) FROM order_totals)
ORDER BY avg_order DESC, c.name;
```

## Complexity

One pass over the lines (layer 1), then small passes over the order and customer summaries. Each layer reduces the row count, which is why layering is both clear and cheap.

## Another way / portable SQL

Nested subqueries in `FROM` do the same but read inside-out. Repeating the average as `AVG(total)` per customer would be simpler, but `spent / n_orders` shows the layering. `WITH a AS (...), b AS (...)` is the same in PostgreSQL and MySQL 8.
