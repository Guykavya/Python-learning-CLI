QUERY = """
SELECT title, category, price,
       ROUND(100.0 * price / SUM(price) OVER (PARTITION BY category), 1) AS pct_category,
       ROUND(100.0 * price / SUM(price) OVER (), 1)                       AS pct_all
FROM books
ORDER BY book_id
"""
