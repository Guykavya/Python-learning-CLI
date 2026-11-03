## Approach

`<>` never gives true for NULL, so add a second branch for the NULL rows.

## Code

```python
QUERY = """
SELECT name
FROM customers
WHERE city <> 'Pune' OR city IS NULL
"""
```

## Complexity

One scan. (With an index on `city`, the engine may need two probes for the OR.)

## Another way / portable SQL

`WHERE COALESCE(city, '') <> 'Pune'` works because a fake empty string is never `'Pune'`. SQLite's `city IS NOT 'Pune'` is null-safe; PostgreSQL spells it `city IS DISTINCT FROM 'Pune'`; MySQL `NOT (city <=> 'Pune')`.
