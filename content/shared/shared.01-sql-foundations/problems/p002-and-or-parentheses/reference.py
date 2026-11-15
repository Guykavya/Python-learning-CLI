QUERY = """
SELECT title FROM books
WHERE (category = 'fiction' OR category = 'mystery') AND price < 13
"""
