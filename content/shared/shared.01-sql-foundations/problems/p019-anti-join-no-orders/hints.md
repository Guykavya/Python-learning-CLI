## Hint 1

Which table must keep all its rows? After a LEFT JOIN, what do the order columns look like for a customer with no orders? Which order column is guaranteed to be non-NULL for a real match (a primary key)?

## Hint 2

```
SELECT c.name
FROM customers AS c
LEFT JOIN orders AS o ON <match on customer_id>
WHERE <o's primary key is NULL>
```

Try `WHERE customer_id NOT IN (SELECT customer_id FROM orders)` on dataset B and see what happens.
