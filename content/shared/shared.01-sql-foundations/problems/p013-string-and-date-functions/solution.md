## Approach

Apply the scalar functions per row. `strftime` returns text, so compare it with `'2022'` (a string), not 2022.

## Code

```python
QUERY_A = """
SELECT title, strftime('%Y', published) AS year, substr(title, 1, 3) AS short, length(title) AS len
FROM books
"""
QUERY_B = """SELECT title FROM books WHERE strftime('%Y', published) = '2022'"""
QUERY_C = """
SELECT title, CAST(julianday('2024-01-01') - julianday(published) AS INTEGER) AS days_old
FROM books
"""
```

## Complexity

One scan each. A function on a column (`strftime(..., published)`) stops a plain index on `published` from being used; `WHERE published >= '2022-01-01' AND published < '2023-01-01'` can use it.

## Another way / portable SQL

B can be written as a range, as noted above (faster with an index). Other databases: `EXTRACT(YEAR FROM published)` (PostgreSQL, MySQL) and `SUBSTRING(title FROM 1 FOR 3)` or `SUBSTR`. SQLite has no `DATEDIFF`; use `julianday`.
