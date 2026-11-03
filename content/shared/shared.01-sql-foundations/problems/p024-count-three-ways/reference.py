QUERY = """
SELECT COUNT(*)             AS total_rows,
       COUNT(city)          AS with_city,
       COUNT(DISTINCT city) AS distinct_cities
FROM customers
"""
