QUERY = """
SELECT oi.order_id, b.title, ROUND(oi.qty * oi.unit_price, 2) AS line_total
FROM order_items AS oi
JOIN orders AS o ON o.order_id = oi.order_id
JOIN books AS b ON b.book_id = oi.book_id
WHERE o.status = 'shipped'
ORDER BY oi.order_id, b.title
"""
