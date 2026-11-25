## Approach

`EXCLUDE` keeps a wide table readable when you need all but one or two columns. `GROUP BY ALL` lets the engine infer the grouping from the non-aggregate columns of the `SELECT`, so adding a column to the `SELECT` cannot leave it out of the `GROUP BY`.

## Code

```python
QUERY = """
WITH e AS (SELECT * EXCLUDE (event_id) FROM events)
SELECT u.channel, u.country, e.event_type, count(*) AS events
FROM e JOIN users u USING (user_id)
GROUP BY ALL
"""
```

## Complexity

One join and one aggregation: O(events).

## Another way

The spelled-out version, `GROUP BY u.channel, u.country, e.event_type` (or `GROUP BY 1, 2, 3`), gives the same rows; the test compares with it. `GROUP BY ALL` is DuckDB (and a few other engines) only. In portable SQL, use positions or names, and expect to edit the `GROUP BY` every time the `SELECT` changes.
