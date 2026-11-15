QUERY_A = """
SELECT email FROM newsletter
UNION
SELECT email FROM buyers
ORDER BY email
"""

QUERY_B = """
SELECT email FROM newsletter
INTERSECT
SELECT email FROM buyers
ORDER BY email
"""

QUERY_C = """
SELECT email FROM newsletter
EXCEPT
SELECT email FROM buyers
ORDER BY email
"""
