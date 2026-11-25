QUERY = """
SELECT date_trunc('month', signup_at)::DATE AS cohort, count(*) AS cohort_size
FROM users
GROUP BY 1
""" 
