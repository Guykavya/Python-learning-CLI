## Hint 1

Split the problem in two. First: which customer ids bought a tech book? (orders -> order_items -> books). Second: which names go with those ids?
Which operator keeps the rows whose id appears in a list of ids?

## Hint 2

```
SELECT name
FROM customers
WHERE customer_id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN books b        ON b.book_id   = oi.book_id
    WHERE b.category = 'tech'
)
ORDER BY name;
```
Fill the gaps yourself before looking: what is joined to what?
