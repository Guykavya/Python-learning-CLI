## Approach

Delete first, so that book 2 (qty 0) is gone and is then created fresh with the delivered quantity. Then `INSERT ... SELECT` with `GROUP BY` sums the deliveries per book, and `ON CONFLICT (book_id) DO UPDATE` adds to existing rows.

## Code

```python
SCRIPT = """
DELETE FROM stock WHERE qty = 0;

INSERT INTO stock (book_id, qty)
SELECT book_id, SUM(qty) FROM incoming GROUP BY book_id
ON CONFLICT (book_id) DO UPDATE SET qty = qty + excluded.qty;
"""
```

## Complexity

Delete: scan of `stock` (or an index on `qty`). Upsert: one aggregation of `incoming`, then O(log n) primary-key probe per distinct book.

## Another way / portable SQL

PostgreSQL has the same `ON CONFLICT ... DO UPDATE` syntax. MySQL spells it `INSERT ... ON DUPLICATE KEY UPDATE qty = qty + VALUES(qty)`. Older SQLite code used `INSERT OR REPLACE`, which deletes and re-inserts the row (and silently resets other columns) - avoid it for "add to" logic.
If `INSERT ... SELECT` without `GROUP BY` gives a parse error with `ON CONFLICT`, add `WHERE true` to the SELECT: SQLite needs it to tell the clause from a join.
