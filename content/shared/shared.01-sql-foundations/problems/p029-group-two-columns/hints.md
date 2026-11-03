## Hint 1

How many pieces of information identify one group here: one column or two? Which two columns must the `GROUP BY` list so that
customer 1's `shipped` orders and `cancelled` orders are counted separately?

## Hint 2

```
SELECT customer_id, status, COUNT(*) AS n_orders
FROM orders
GROUP BY ?, ?
ORDER BY n_orders ?, customer_id ?, status ?;
```
Check: you may sort by an alias of an aggregate (`n_orders`), because `ORDER BY` runs after `SELECT`.
