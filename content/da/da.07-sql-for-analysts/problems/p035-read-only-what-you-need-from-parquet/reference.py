def june_revenue(con, path):
    sql = f"""
        SELECT COALESCE(sum(amount), 0)
        FROM read_parquet('{path}')
        WHERE order_time >= TIMESTAMP '2025-06-01' AND order_time < TIMESTAMP '2025-07-01'
    """
    return con.execute(sql).fetchall()[0][0]
