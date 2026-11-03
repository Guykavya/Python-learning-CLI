## Hint 1

Which table is the "centre" that links to the other two? Which columns connect `order_items` to `orders`, and `order_items` to `books`? Where does the `shipped` condition go, and which table's column is it?

## Hint 2

```
SELECT oi.order_id, b.title, ROUND(oi.qty * oi.unit_price, 2) AS line_total
FROM order_items AS oi
JOIN orders AS o ON <oi.order_id = o.order_id>
JOIN books  AS b ON <oi.book_id = b.book_id>
WHERE o.status = 'shipped'
ORDER BY ...
```
