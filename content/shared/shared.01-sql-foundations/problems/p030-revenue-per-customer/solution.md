## Approach

Chain two inner joins: customers to orders, orders to order_items. `WHERE` drops cancelled orders before grouping. Sum the expression `qty * unit_price` per customer. Customers without a qualifying order have no joined rows, so they vanish (that is what the statement asks).

## Code

```sql
SELECT c.name,
       ROUND(SUM(oi.qty * oi.unit_price), 2) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC, c.name;
```

## Complexity

The join produces one row per order line (the "finest" table); the group then folds them. With indexes on `orders.customer_id` and `order_items.order_id` this is about O(lines). Grouping by the primary key plus the name is the portable form for PostgreSQL.

## Another way / portable SQL

Start from `order_items` and join upward; the result is the same. If you also needed customers with zero revenue you would switch to `LEFT JOIN` and move the status condition into `ON` (see the LEFT JOIN problems).
