## Approach

Functions can be nested; the inner one runs first. C first converts `''` to NULL and then gives every NULL the default.

## Code

```python
QUERY_A = """SELECT name, COALESCE(city, 'unknown') AS city FROM customers"""
QUERY_B = """SELECT name, NULLIF(city, '') AS city FROM customers"""
QUERY_C = """SELECT name, COALESCE(NULLIF(city, ''), 'unknown') AS city FROM customers"""
```

## Complexity

Constant work per row; one scan.

## Another way / portable SQL

`CASE WHEN city IS NULL OR city = '' THEN 'unknown' ELSE city END` does the same as C. COALESCE and NULLIF are standard and portable. (Oracle treats `''` as NULL; most others do not.)
