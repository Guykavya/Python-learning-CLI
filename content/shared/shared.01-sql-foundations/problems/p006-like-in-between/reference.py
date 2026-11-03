QUERY_A = """
SELECT title FROM books WHERE title LIKE 'S%'
"""

QUERY_B = """
SELECT title FROM books WHERE category IN ('tech', 'cooking')
"""

QUERY_C = """
SELECT title FROM books WHERE price BETWEEN 10 AND 18
"""
