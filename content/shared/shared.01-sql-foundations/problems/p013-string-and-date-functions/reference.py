QUERY_A = """
SELECT title, strftime('%Y', published) AS year, substr(title, 1, 3) AS short, length(title) AS len FROM books
"""

QUERY_B = """
SELECT title FROM books WHERE strftime('%Y', published) = '2022'
"""

QUERY_C = """
SELECT title, CAST(julianday('2024-01-01') - julianday(published) AS INTEGER) AS days_old FROM books
"""
