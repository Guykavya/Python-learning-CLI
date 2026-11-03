QUERY = """
WITH book_sales AS (
    SELECT book_id, SUM(qty) AS units
    FROM order_items
    GROUP BY book_id
)
SELECT b.title, s.units
FROM books b
JOIN book_sales s ON s.book_id = b.book_id
WHERE s.units >= 2
ORDER BY s.units DESC, b.title
"""
