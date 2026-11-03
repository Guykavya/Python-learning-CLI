QUERY = """
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
ORDER BY c.name
"""
