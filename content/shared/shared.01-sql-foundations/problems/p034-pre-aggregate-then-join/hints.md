## Hint 1

After you join lines and payments to the same order, how many rows does order 101 produce (2 lines, 2 payments)? What would
make each side have exactly one row per order before the join?

## Hint 2

```
SELECT o.order_id,
       COALESCE(i.items_total, 0.0) AS items_total,
       COALESCE(p.paid,        0.0) AS paid
FROM orders o
LEFT JOIN ( SELECT order_id, SUM(qty*unit_price) AS items_total
            FROM order_items GROUP BY order_id ) i ON i.order_id = o.order_id
LEFT JOIN ( SELECT order_id, SUM(?) AS paid
            FROM payments GROUP BY ? ) p ON p.order_id = o.order_id
ORDER BY o.order_id;
```
