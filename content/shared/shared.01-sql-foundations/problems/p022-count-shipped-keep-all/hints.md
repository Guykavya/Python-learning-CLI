## Hint 1

Which join type keeps customers that have no matching order? Where must the `shipped` test live so that a customer whose orders are all pending is not thrown away: in `ON` or in `WHERE`? For a customer with no match, the order columns are NULL: which of `COUNT(*)` and `COUNT(o.order_id)` then gives 0?

## Hint 2

```
SELECT c.name, COUNT(<order column>) AS shipped_orders
FROM customers AS c
LEFT JOIN orders AS o ON <customer match> AND <status test>
GROUP BY c.customer_id        -- or c.name if names are unique
```
