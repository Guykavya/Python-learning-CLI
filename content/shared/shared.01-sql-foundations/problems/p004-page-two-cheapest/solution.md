## Approach

Sort fully, skip `(2 - 1) * 3 = 3` rows, keep 3. The `title` tie-break makes the order deterministic, so the same row never appears on two pages.

## Code

```python
QUERY = """
SELECT title
FROM books
ORDER BY price, title
LIMIT 3 OFFSET 3
"""
```

## Complexity

The engine still sorts (or walks an index) and discards the first 3 rows, so a deep page costs more than page 1: OFFSET is O(offset + limit). For huge tables use keyset paging (`WHERE price > last_price ...`).

## Another way / portable SQL

`LIMIT 3, 3` is SQLite/MySQL shorthand (offset first). PostgreSQL and the standard also allow `OFFSET 3 ROWS FETCH NEXT 3 ROWS ONLY`.
