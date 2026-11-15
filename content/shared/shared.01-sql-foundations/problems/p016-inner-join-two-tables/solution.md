## Approach

Join on the key pair. Table aliases (`b`, `a`) make column names short and unambiguous.

## Code

```python
QUERY = """
SELECT b.title, a.name AS author
FROM books AS b
INNER JOIN authors AS a ON a.author_id = b.author_id
"""
```

## Complexity

The engine usually loops over one table and looks up matches in the other using the primary key of `authors` (an index), about O(n log m). Without an index it would compare every pair (O(n*m)).

## Another way / portable SQL

`FROM books b, authors a WHERE a.author_id = b.author_id` is the old comma style: same result, but easy to turn into an accidental cross join. `INNER JOIN` and plain `JOIN` mean the same in all databases.
