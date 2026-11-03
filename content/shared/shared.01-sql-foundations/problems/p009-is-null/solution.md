## Approach

`IS NULL` and `IS NOT NULL` are the only comparisons that can be true for NULL. A row passes `WHERE` only when the condition is **true**, so `= NULL` (unknown) drops every row.

## Code

```python
QUERY_A = """SELECT title FROM books WHERE pages IS NULL"""
QUERY_B = """SELECT title FROM books WHERE pages IS NOT NULL"""
```

## Complexity

One scan each. An index can find NULLs in SQLite, MySQL and PostgreSQL.

## Another way / portable SQL

`NOT (pages IS NULL)` is equivalent. `pages ISNULL` and `pages NOTNULL` are SQLite/PostgreSQL shorthand; do not rely on them in MySQL. Never write `pages != NULL`.
