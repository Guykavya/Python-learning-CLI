## Hint 1

For step 2, which query returns the ids of customers with at least two orders? How can an `UPDATE`'s `WHERE` use that list?

## Hint 2

```
UPDATE books SET price = ROUND(price * 1.10, 2) WHERE category = 'Tech';
UPDATE customers SET tier = 'gold'
WHERE customer_id IN (SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*) >= 2);
```
