## Approach

```python
def uses_index(db, sql, params=()):
    rows = db.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return any("SEARCH" in row[3] for row in rows)
```

`EXPLAIN QUERY PLAN` accepts the same placeholders and parameters as the query. Looking for the word `SEARCH` anywhere is enough for "an index (or the primary key) is used for at least one table". A `SCAN ... USING COVERING INDEX` line is still a scan: it reads the whole index, so it does not count.

Example: `WHERE city = ?` has no index on `city`: the plan is `SCAN users`, so the answer is `False`.

## Complexity

`O(1)`: planning only.

## Another way

For several tables, require every table to be searched: look at all lines that start with `SCAN` and refuse if any is on a big table.

## Why it matters

The first thing to do about a slow query is to read its plan. A query that scans a million rows on every request is the most common database performance bug.
