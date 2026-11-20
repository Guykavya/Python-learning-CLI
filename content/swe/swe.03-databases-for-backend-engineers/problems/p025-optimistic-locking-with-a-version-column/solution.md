## Approach

```python
def update_price(db, product_id, new_price_paise, seen_version):
    with db:
        cur = db.execute(
            "UPDATE products SET price_paise = ?, version = version + 1 WHERE id = ? AND version = ?",
            (new_price_paise, product_id, seen_version))
    return cur.rowcount == 1
```

The version check and the change are one statement, so no gap exists between "is it still version N?" and "change it". `version = version + 1` makes the next save with the old number fail. The caller reacts to `False` by reloading the row and asking the user (or merging).

Example: editor A saves with version 1: one row matches, price changes, version becomes 2, result `True`. Editor B saves with version 1: `WHERE ... version = 1` matches nothing, `rowcount` is 0, result `False`, and A's price is safe.

## Complexity

`O(1)`.

## Another way

HTTP does the same with `ETag` and `If-Match` (an API returns `412 Precondition Failed`). **Pessimistic** locking (`SELECT ... FOR UPDATE`) locks the row while a human edits: simple, but holds locks for minutes.

## Why it matters

"Last writer wins" silently destroys work. Optimistic locking costs one column and gives you a clear conflict to handle.
