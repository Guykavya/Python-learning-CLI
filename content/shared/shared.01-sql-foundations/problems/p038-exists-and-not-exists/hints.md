## Hint 1

For each customer row, which question do you ask the `orders` table? Which column ties the subquery to the *outer* customer?
For books, which table would contain a row proving the book was ordered, and what should `NOT EXISTS` say about it?

## Hint 2

```
QUERY_A:
SELECT c.name FROM customers c
WHERE EXISTS ( SELECT 1 FROM orders o
               WHERE o.customer_id = c.? AND o.status = ? )
ORDER BY c.name;

QUERY_B:
SELECT b.title FROM books b
WHERE NOT EXISTS ( SELECT 1 FROM order_items oi WHERE oi.book_id = b.? )
ORDER BY b.title;
```
