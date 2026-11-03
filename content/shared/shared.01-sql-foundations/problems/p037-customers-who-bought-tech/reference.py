QUERY = """
SELECT name
FROM customers
WHERE customer_id IN (
    SELECT o.customer_id
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    JOIN books b        ON b.book_id   = oi.book_id
    WHERE b.category = 'tech'
)
ORDER BY name
"""
