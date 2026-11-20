## Hint 1

What does the second editor know? Only the version they saw. How can the `UPDATE` itself check that nothing changed since?

## Hint 2

Put the version in the `WHERE`. If someone else already saved, the version is different and the statement matches **no row**. How do you see that from Python?

## Hint 3

```text
UPDATE products SET price_paise = ?, version = version + 1 WHERE id = ? AND version = ?
return cursor.rowcount == 1       (inside "with db:" so it is committed)
```
