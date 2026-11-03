## Approach

Authors are the "keep everything" side, so they go on the left. Matching books are attached; Zed Park gets `NULL`.

## Code

```python
QUERY = """
SELECT a.name AS author, b.title
FROM authors AS a
LEFT JOIN books AS b ON b.author_id = a.author_id
"""
```

## Complexity

Like an inner join (a lookup per author), but rows without a match are kept rather than discarded.

## Another way / portable SQL

`books RIGHT JOIN authors` gives the same rows (RIGHT JOIN needs SQLite 3.39+; MySQL and PostgreSQL have it). Most people just swap the tables and use LEFT JOIN. `LEFT OUTER JOIN` is the same as `LEFT JOIN`.
