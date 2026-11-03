## Hint 1

For one customer, how would you find the id of the latest order if you could only write one small query? (Think `ORDER BY` and `LIMIT`.)
How can you make the tie-break (same date, larger id) part of that ordering? Then how do you use that id from the outer query?

## Hint 2

```
SELECT c.name, o.order_id, o.ordered
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id = (
    SELECT o2.order_id
    FROM orders o2
    WHERE o2.customer_id = c.customer_id        -- the correlation
    ORDER BY o2.ordered ?, o2.order_id ?
    LIMIT 1
)
ORDER BY c.name;
```
