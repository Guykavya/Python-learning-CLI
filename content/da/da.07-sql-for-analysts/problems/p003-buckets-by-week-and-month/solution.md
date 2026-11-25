## Approach

`date_trunc` rounds a timestamp down to the start of its unit, so all timestamps of the same week or month get the same value and a `GROUP BY` on it counts them together. The two grains (week, month) live in one result with a label column and `UNION ALL`.

## Code

```python
QUERY = """
SELECT 'week' AS period, date_trunc('week', signup_at)::DATE AS period_start, count(*) AS signups
FROM users GROUP BY 2
UNION ALL
SELECT 'month', date_trunc('month', signup_at)::DATE, count(*)
FROM users GROUP BY 2
"""
```

## Complexity

Two passes over `users`: O(users).

## Another way

`GROUP BY GROUPING SETS` can do both groupings in one scan, but needs a `CASE` to build the labels; `UNION ALL` is easier to read. Never use `UNION` (without `ALL`) here: it removes duplicate rows, which would silently merge two buckets that happen to have the same count and start.
