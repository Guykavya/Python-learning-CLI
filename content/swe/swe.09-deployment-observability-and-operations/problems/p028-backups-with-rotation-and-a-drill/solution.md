## Approach

```python
def backup(db_file, backup_dir, keep=7, now=time.time):
    ...
    try:
        with closing(sqlite3.connect(f"{db_file.resolve().as_uri()}?mode=ro", uri=True)) as source, \
                closing(sqlite3.connect(target)) as copy:
            source.backup(copy)
            verdict = copy.execute("PRAGMA integrity_check").fetchone()[0]
    except sqlite3.DatabaseError as exc:
        verdict = f"{type(exc).__name__}: {exc}"
    if verdict != "ok":
        target.unlink(missing_ok=True)
        raise RuntimeError(f"backup FAILED: {verdict}")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    Path(f"{target}.sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
    for old in sorted(backup_dir.glob(f"{db_file.stem}-*.db"))[:-keep]:
        old.unlink()
        Path(f"{old}.sha256").unlink(missing_ok=True)
    return target, digest
```

and `drill` restores into a temporary folder and answers the four questions of the chapter: is the file the one we wrote (checksum), does it restore and pass SQLite's own integrity check, does the expected table exist, is the **data** there (a minimum row count catches an empty or ancient backup). Opening the source with `mode=ro` means a typo in the path cannot create an empty database that then "backs up" fine.

Why the timestamped names sort correctly: `20231114T221320Z` is fixed-width and most significant first, so alphabetical order is time order, which makes `sorted(...)[:-keep]` a correct retention rule.

## Complexity

O(size of the database) for the copy and for the checksum; the rotation is O(number of backups).

## Another way

For PostgreSQL the same discipline uses `pg_dump` and `pg_restore` (chapter 13.3, run on your machine). Copying the file while the app writes is wrong for SQLite; `VACUUM INTO 'file'` is another way to write a consistent copy. Off-machine copy, encryption and a "dead-man's switch" ping (chapter 13.4) are what turn this function into a routine.
