## Approach

Two window sums: one partitioned by category, one over the whole result. Each row divides its own price by those. `100.0 *` forces decimal arithmetic.

## Code

```python
QUERY = """
SELECT title, category, price,
       ROUND(100.0 * price / SUM(price) OVER (PARTITION BY category), 1) AS pct_category,
       ROUND(100.0 * price / SUM(price) OVER (), 1)                       AS pct_all
FROM books
ORDER BY book_id
"""
```

## Complexity

One pass plus a sort per partition, O(n log n). No self join, so no n x n blow-up.

## Another way / portable SQL

Use a scalar subquery for the grand total: `price / (SELECT SUM(price) FROM books)`, and a join to a pre-aggregated category CTE for the category share. Both are portable to every database; the window version is shorter. In PostgreSQL use `ROUND(x::numeric, 1)` (it has no `ROUND(double, int)`).
