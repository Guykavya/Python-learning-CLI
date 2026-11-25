def revenue_by_plan(con, orders):
    con.register("orders", orders)
    return con.execute("""
        SELECT plan, count(*) AS orders, sum(amount) AS revenue
        FROM orders GROUP BY plan ORDER BY revenue DESC, plan
    """).df()
