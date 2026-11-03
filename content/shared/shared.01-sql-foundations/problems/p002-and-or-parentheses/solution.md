## Approach

The category test is an OR of two equalities. The price test applies to both, so the OR is wrapped in
parentheses and joined to the price test with AND.

## Code

```python
QUERY = """
SELECT title
FROM books
WHERE (category = 'fiction' OR category = 'mystery')
  AND price < 13
"""
```

## Complexity

One scan, each row tested once. The WHERE is cheap per row.

## Another way / portable SQL

`WHERE category IN ('fiction', 'mystery') AND price < 13` removes the need for parentheses.
`IN` is portable (SQLite, MySQL, PostgreSQL).
