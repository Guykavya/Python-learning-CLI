## Hint 1

Write and run each layer alone before you add the next. Which table do you group to get an order's total? Which result do you group to get
a customer's count and spent? And what must the "average of all orders" be computed from: customers or `order_totals`?

## Hint 2

```
WITH order_totals AS (
    SELECT o.order_id, o.customer_id, SUM(oi.qty * oi.unit_price) AS total
    FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id, o.customer_id
),
customer_stats AS (
    SELECT customer_id, COUNT(*) AS n_orders, SUM(total) AS spent
    FROM order_totals GROUP BY customer_id
)
SELECT c.name, s.n_orders, s.spent, ROUND(s.spent * 1.0 / s.n_orders, 2) AS avg_order
FROM customer_stats s JOIN customers c ON c.customer_id = s.customer_id
WHERE s.spent * 1.0 / s.n_orders > ( SELECT AVG(?) FROM order_totals )
ORDER BY avg_order DESC, c.name;
```
