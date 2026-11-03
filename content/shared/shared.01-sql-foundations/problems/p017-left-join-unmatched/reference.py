QUERY = """
SELECT a.name AS author, b.title FROM authors AS a LEFT JOIN books AS b ON b.author_id = a.author_id
"""
