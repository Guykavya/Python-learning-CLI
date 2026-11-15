QUERY_A = """
SELECT c.name
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o
              WHERE o.customer_id = c.customer_id AND o.status = 'shipped')
ORDER BY c.name
"""

QUERY_B = """
SELECT b.title
FROM books b
WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.book_id = b.book_id)
ORDER BY b.title
"""
