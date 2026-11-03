## Approach

Start from `order_items` (one row per line) and attach the order (for status) and the book (for title). Filter with `WHERE`, compute the total in the select list and round it to cents (floating point can give `29.970000000000002`).

## Code

```python
QUERY = """
SELECT oi.order_id, b.title, ROUND(oi.qty * oi.unit_price, 2) AS line_total
FROM order_items AS oi
JOIN orders AS o ON o.order_id = oi.order_id
JOIN books  AS b ON b.book_id  = oi.book_id
WHERE o.status = 'shipped'
ORDER BY oi.order_id, b.title
"""
```

## Complexity

Two key lookups per order line (the primary keys of `orders` and `books`), then a sort of the matching lines. The planner may reorder the joins.

## Another way / portable SQL

Join order does not matter for inner joins; the result is the same. For money, real databases use `NUMERIC`/`DECIMAL` (PostgreSQL, MySQL) or integer cents instead of floating point `REAL`.
