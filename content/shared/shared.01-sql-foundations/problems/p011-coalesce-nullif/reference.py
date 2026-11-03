QUERY_A = """
SELECT name, COALESCE(city, 'unknown') AS city FROM customers
"""

QUERY_B = """
SELECT name, NULLIF(city, '') AS city FROM customers
"""

QUERY_C = """
SELECT name, COALESCE(NULLIF(city, ''), 'unknown') AS city FROM customers
"""
