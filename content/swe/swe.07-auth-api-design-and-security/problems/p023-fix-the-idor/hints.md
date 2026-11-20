## Hint 1

Read the three marked lines. Each has a `user_id` available (it comes from the token) that the SQL never uses. What question does the database answer today, and what question should it answer?

## Hint 2

You do not need an `if` after the query. Put the owner into the `WHERE` clause, so the database itself finds nothing for somebody else's id. For the write endpoints, how do you know that nothing matched? Look at `cur.rowcount`, which the code already uses.

## Hint 3

```text
SELECT ... WHERE id = ? AND owner_id = ?     args: (note_id, user_id)
UPDATE ... WHERE id = ? AND owner_id = ?     args: (text, note_id, user_id)
DELETE ... WHERE id = ? AND owner_id = ?     args: (note_id, user_id)
No row / rowcount 0 -> the existing 404 note not found
```
