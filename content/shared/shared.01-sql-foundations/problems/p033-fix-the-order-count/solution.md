## Approach

The join makes one row per order line, so `COUNT(*)` counts lines. Count the distinct order ids instead. `SUM(qty * unit_price)` is a sum over lines, so it is unaffected.

## Code

```sql
SELECT c.name,
       COUNT(DISTINCT o.order_id)            AS n_orders,
       ROUND(SUM(oi.qty * oi.unit_price), 2) AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
GROUP BY c.customer_id, c.name
ORDER BY c.name;
```

## Complexity

`COUNT(DISTINCT ...)` keeps the set of seen order ids per group, a little extra memory. Same O(lines) scan as before.

## Another way / portable SQL

Pre-aggregate: count orders in a subquery on `orders` and join it to a per-customer revenue subquery. Safer when you add more joined tables, because `COUNT(DISTINCT)` does not help with `SUM` columns that sit on the order (like a shipping fee). Works the same in MySQL and PostgreSQL.
