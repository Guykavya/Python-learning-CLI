## Approach

After the LEFT JOIN, customers without orders have NULL in every `o.*` column. Testing the primary key `o.order_id IS NULL` selects exactly those.

## Code

```python
QUERY = """
SELECT c.name
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
"""
```

## Complexity

One lookup per customer in `orders.customer_id` (fast with an index on that column). Customers with many orders are discarded after the join, so on huge tables `NOT EXISTS` can be cheaper.

## Another way / portable SQL

`WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id)` is the safest form and is portable. `NOT IN (SELECT customer_id FROM orders)` is **wrong** when the subquery contains a NULL: it returns no rows at all (three-valued logic).
