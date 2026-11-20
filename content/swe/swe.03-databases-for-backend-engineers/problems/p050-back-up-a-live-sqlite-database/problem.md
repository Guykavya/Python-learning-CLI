# Back up a live SQLite database

Chapter section 15.2. The easy way to back up a SQLite file is to copy it: `shutil.copyfile(src, dst)`. It is **wrong while the database is in use**: another connection may be in the middle of a transaction, some pages of the file are already new and others old, and the journal that would repair the file is not copied. You get a backup that is **corrupt or inconsistent**, and you only find out when you need it.

`starter.py` has exactly that mistake. Write

```python
backup(src_path, dst_path)
```

using the **online backup API** of `sqlite3` (`source_connection.backup(target_connection)`), which copies a **consistent snapshot of the committed data**, even while others write.

- If `dst_path` already exists, raise `FileExistsError` and touch nothing (never overwrite a backup by accident).
- Close both connections before returning, also when something fails.
- The backup opens as a normal database, `PRAGMA integrity_check` says `ok`, and it contains **only committed** data: rows of a transaction that is still open when the backup runs are not in it.

## Example

```python
backup("shop.db", "backups/shop-2026-01-05.db")
```
