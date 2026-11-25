## Approach

Aggregate first, then use windows over the aggregated rows. `sum(revenue) OVER ()` is the grand total on every row. The running sum needs an `ORDER BY` that includes the tie-breakers, and a `ROWS` frame so that tied rows are not added together as peers (with the default `RANGE` frame two tied rows would show the same cumulative share).

## Code

```python
QUERY = """
WITH g AS (
  SELECT o.plan, u.country, sum(o.amount) AS revenue
  FROM orders o JOIN users u USING (user_id)
  GROUP BY o.plan, u.country
)
SELECT plan, country, revenue,
       revenue * 1.0 / sum(revenue) OVER () AS share,
       sum(revenue) OVER (ORDER BY revenue DESC, plan, country ROWS UNBOUNDED PRECEDING) * 1.0
         / sum(revenue) OVER () AS cumulative_share
FROM g
ORDER BY revenue DESC, plan, country
"""
```

## Complexity

O(n log n) for the sort of the groups.

## Another way

`percent_rank` and `cume_dist` are close relatives but rank *rows*, not money. A "Pareto" table (the top groups that give 80 percent of revenue) is simply this query with `WHERE cumulative_share <= 0.8` in an outer query (or `QUALIFY`).

## Pitfall to remember

`revenue / sum(revenue)` with the default frame and ties: the first two tied rows would both get the cumulative share of the second. Put `ROWS` in the frame when you need a strict running order.
