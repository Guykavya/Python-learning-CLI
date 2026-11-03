## Approach

Sort keys apply left to right. `DESC` attaches to `price` alone, so `category` and `title` stay ascending.

## Code

```python
QUERY = """
SELECT category, title, price
FROM books
ORDER BY category, price DESC, title
"""
```

## Complexity

The engine must sort: about n log n comparisons. An index on `(category, price DESC, title)` could return rows already in order and skip the sort.

## Another way / portable SQL

You can sort by position (`ORDER BY 1, 3 DESC, 2`), but names are clearer. Portable across SQLite, MySQL and PostgreSQL.
