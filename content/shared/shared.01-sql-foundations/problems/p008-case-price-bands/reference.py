QUERY = """
SELECT title,
 CASE WHEN price < 10 THEN 'budget' WHEN price < 20 THEN 'standard' ELSE 'premium' END AS band
FROM books
"""
