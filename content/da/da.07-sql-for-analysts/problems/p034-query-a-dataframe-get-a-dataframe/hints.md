## Hint 1

How does the connection get to know the DataFrame, and under which name must the SQL mention it? Which method of the result turns it into a DataFrame without leaving anything unfinished on the connection?

## Hint 2

```text
def revenue_by_plan(con, orders):
    con.register("orders", orders)
    return con.execute("SELECT plan, count(*) AS orders, sum(amount) AS revenue FROM orders GROUP BY plan ORDER BY revenue DESC, plan").df()
```

Registering again with the same name replaces the earlier DataFrame.
