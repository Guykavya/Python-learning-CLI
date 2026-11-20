## Approach

```python
def conflicting_facts(rows, key, field):
    seen = {}
    for row in rows:
        values = seen.setdefault(row[key], [])
        if row[field] not in values:
            values.append(row[field])
    return {k: v for k, v in seen.items() if len(v) > 1}
```

One pass over the rows; a list per key holds the distinct values in first-seen order. Only keys with two or more values are returned. Example: customer `c2` has two e-mail addresses, so the table does not say which one is true. That is an **update anomaly**: someone changed one row and forgot the other.

## Complexity

`O(rows * distinct values per key)`.

## Another way

Use a `set` per key and sort at the end; you lose the first-seen order. In SQL: `SELECT customer FROM flat GROUP BY customer HAVING COUNT(DISTINCT email) > 1`.

## Why it matters

The cure is not a better check but a better schema: store the e-mail **once**, in a `customers` table (problem 3).
