QUERY = """
SELECT category, COUNT(*) AS n_books, ROUND(AVG(price), 2) AS avg_price
FROM books
GROUP BY category
ORDER BY category
"""
