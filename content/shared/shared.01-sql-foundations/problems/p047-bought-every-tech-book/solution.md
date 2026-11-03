## Approach

Division by double negation: a customer is kept if there is **no** tech book for which **no** purchase by that customer exists. As soon as one tech book is unbought, the test fails for that customer. A customer with no purchases at all fails it too (as long as the shop has at least one tech book).

The counting version joins customers to their tech lines, groups by customer, and requires `COUNT(DISTINCT book_id)` to equal the number of tech books. `DISTINCT` is essential because a book can be bought several times.

## Code

```sql
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1
    FROM books b
    WHERE b.category = 'tech'
      AND NOT EXISTS (
          SELECT 1
          FROM orders o
          JOIN order_items oi ON oi.order_id = o.order_id
          WHERE o.customer_id = c.customer_id
            AND oi.book_id = b.book_id
      )
)
ORDER BY c.name;
```

## Complexity

Roughly customers x tech books probes, each a lookup in the customer's order lines. With indexes on `orders(customer_id)` and `order_items(order_id, book_id)` each probe is fast. The counting version is one grouped scan: O(lines).

## Another way / portable SQL

```sql
SELECT c.name
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
JOIN books b        ON b.book_id = oi.book_id AND b.category = 'tech'
GROUP BY c.customer_id, c.name
HAVING COUNT(DISTINCT b.book_id) = (SELECT COUNT(*) FROM books WHERE category = 'tech')
ORDER BY c.name;
```
Both forms are portable. If the category had **no** books, the double `NOT EXISTS` would return every customer (vacuous truth), while the counting version would return nobody: decide which you want.
