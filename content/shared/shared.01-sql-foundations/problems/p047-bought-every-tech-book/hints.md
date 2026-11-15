## Hint 1

Instead of "bought all", try to phrase the opposite: "there is a tech book that this customer did **not** buy". A customer qualifies when that
sentence is false. Which operator expresses "there is no ..." and can it be nested inside itself?

Alternative: how many tech books are there, and how many *different* tech books did each customer buy?

## Hint 2

```
-- double NOT EXISTS
SELECT c.name FROM customers c
WHERE NOT EXISTS (                                  -- no tech book ...
    SELECT 1 FROM books b WHERE b.category = 'tech'
    AND NOT EXISTS (                                -- ... that the customer did not buy
        SELECT 1 FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.customer_id = c.customer_id AND oi.book_id = b.?
    )
)
ORDER BY c.name;
-- counting version: GROUP BY customer, HAVING COUNT(DISTINCT tech book ids) = (SELECT COUNT(*) FROM books WHERE category='tech')
```
