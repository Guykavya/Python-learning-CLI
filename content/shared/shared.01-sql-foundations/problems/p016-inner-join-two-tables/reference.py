QUERY = """
SELECT b.title, a.name AS author FROM books AS b INNER JOIN authors AS a ON a.author_id = b.author_id
"""
