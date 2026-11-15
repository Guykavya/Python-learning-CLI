QUERY_A = """
SELECT title FROM books WHERE pages IS NULL
"""

QUERY_B = """
SELECT title FROM books WHERE pages IS NOT NULL
"""
