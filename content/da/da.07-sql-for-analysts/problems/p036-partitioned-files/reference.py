def revenue_by_country(con, folder):
    sql = f"""
        SELECT country, sum(amount) AS revenue
        FROM read_parquet('{folder}/**/*.parquet', hive_partitioning = true)
        GROUP BY country ORDER BY country
    """
    return con.execute(sql).fetchall()
