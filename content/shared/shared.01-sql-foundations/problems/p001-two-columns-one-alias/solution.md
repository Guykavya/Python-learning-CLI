## Approach

`FROM books` reads every row. The select list names the two output columns. `price AS cost` renames
the second one in the result only; the table itself is unchanged.

## Code

```python
QUERY = """
SELECT title, price AS cost
FROM books
"""
```

## Complexity

One pass over the table (a full table scan): the engine reads each of the n rows once and copies two
values out of it. Without a `WHERE`, no index could help anyway.

## Another way / portable SQL

`SELECT title, price cost FROM books` also works (the `AS` keyword is optional in SQLite, MySQL and
PostgreSQL), but writing `AS` is clearer. For a name with spaces, use quotes: `AS "unit cost"`.
