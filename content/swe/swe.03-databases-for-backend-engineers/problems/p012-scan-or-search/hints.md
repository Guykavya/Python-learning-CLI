## Hint 1

Put `EXPLAIN QUERY PLAN` in front of the query text and run it like a normal query. What does it return?

## Hint 2

The text you want is in the fourth column (`row[3]`). One query can produce several rows (one per table, plus sorting steps).

## Hint 3

```text
rows = db.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
return any("SEARCH" in row[3] for row in rows)
```
