## Approach

Register the DataFrame, run one aggregate query, ask for `.df()`. `register` makes a view over the DataFrame (nothing is copied); registering the same name again replaces it, which is why a second call sees new data.

## Code

```python
def revenue_by_plan(con, orders):
    con.register("orders", orders)
    return con.execute("""
        SELECT plan, count(*) AS orders, sum(amount) AS revenue
        FROM orders GROUP BY plan ORDER BY revenue DESC, plan
    """).df()
```

## Complexity

O(n) for the aggregation plus a sort of the groups.

## Another way

`con.sql(query).df()` builds a lazy relation and runs when you ask for the result. `duckdb.sql(...)` with no connection uses a hidden default connection and finds DataFrames by their Python variable name (a *replacement scan*): convenient in a notebook, risky in library code. Note that `sum` of integers comes back as `float64` in the DataFrame (DuckDB's wide integer type): use `.astype("int64")` when you need integers.
