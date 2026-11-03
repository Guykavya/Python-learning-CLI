QUERY = """
SELECT author_id, COUNT(*) AS n_books
FROM books
GROUP BY author_id
HAVING COUNT(*) >= 2
ORDER BY n_books DESC, author_id
"""
