## Approach

Each query is one predicate on `books`.

## Code

```python
QUERY_A = """SELECT title FROM books WHERE title LIKE 'S%'"""
QUERY_B = """SELECT title FROM books WHERE category IN ('tech', 'cooking')"""
QUERY_C = """SELECT title FROM books WHERE price BETWEEN 10 AND 18"""
```

## Complexity

All three scan the table. A `LIKE` with a fixed prefix (`'S%'`) can use an index on `title`; `'%S'` cannot.

## Another way / portable SQL

`BETWEEN` and `IN` are portable. `LIKE` is case-insensitive for ASCII letters in SQLite and MySQL, but case-sensitive in PostgreSQL (use `ILIKE` there).
