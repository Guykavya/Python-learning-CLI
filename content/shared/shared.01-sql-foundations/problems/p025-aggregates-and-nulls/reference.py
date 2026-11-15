QUERY = """
SELECT SUM(pages)              AS total_pages,
       AVG(pages)              AS avg_known,
       MIN(pages)              AS shortest,
       MAX(pages)              AS longest,
       AVG(COALESCE(pages, 0)) AS avg_if_zero
FROM books
"""
