## Hint 1

Which path leads from a customer to the price of a book line: which table holds the customer, which holds the status, which holds
qty and unit_price? Which column connects each pair of tables? Where does the cancelled filter belong: before or after grouping?

## Hint 2

```
SELECT c.name, ROUND( SUM(oi.qty * oi.unit_price), 2 ) AS revenue
FROM customers c
JOIN orders o       ON o.? = c.?
JOIN order_items oi ON oi.? = o.?
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id            -- or c.name, if names are unique
ORDER BY revenue DESC, c.name;
```
