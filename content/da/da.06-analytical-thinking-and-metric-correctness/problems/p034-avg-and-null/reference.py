QUERY = """
SELECT technician,
       COUNT(rating)          AS rated,
       ROUND(AVG(rating), 2)  AS avg_rating
FROM visits
GROUP BY technician
ORDER BY technician
"""
