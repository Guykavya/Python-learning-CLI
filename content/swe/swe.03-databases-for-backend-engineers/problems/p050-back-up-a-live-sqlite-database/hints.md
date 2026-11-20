## Hint 1

Why can a plain file copy fail? Think of what the database file looks like in the middle of a write transaction, and what SQLite itself knows that a file copy does not.

## Hint 2

`sqlite3.Connection.backup(target)` copies from the connection it is called on into another connection, page by page, under SQLite's own locking. Open both files with `sqlite3.connect`.

## Hint 3

```text
if os.path.exists(dst): raise FileExistsError
source = sqlite3.connect(src); target = sqlite3.connect(dst)
try: source.backup(target)
finally: target.close(); source.close()
```
