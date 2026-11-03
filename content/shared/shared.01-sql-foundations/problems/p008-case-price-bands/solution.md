## Approach

Order the `WHEN` branches from the lowest band up. Since only the first true branch runs, each later branch can drop the lower bound.

## Code

```python
QUERY = """
SELECT title,
       CASE
         WHEN price < 10 THEN 'budget'
         WHEN price < 20 THEN 'standard'
         ELSE 'premium'
       END AS band
FROM books
"""
```

## Complexity

One pass; the CASE is evaluated per row with at most 2 comparisons.

## Another way / portable SQL

`CASE` is standard SQL and works everywhere. The "searched" form (above) is the general one; the "simple" form `CASE category WHEN 'tech' THEN ...` only tests equality.
