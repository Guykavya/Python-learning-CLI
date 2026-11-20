## Approach

```python
import os
import sqlite3


def backup(src_path, dst_path):
    if os.path.exists(dst_path):
        raise FileExistsError(dst_path)
    source = sqlite3.connect(src_path)
    target = sqlite3.connect(dst_path)
    try:
        source.backup(target)              # the online backup API: a consistent snapshot of committed data
    finally:
        target.close()
        source.close()
```

`Connection.backup` reads the source with SQLite's locking rules: it sees **committed** pages only and keeps the copy consistent (if the source changes while it runs, SQLite restarts the affected part). The target is written as a normal database, so the result is a valid file at one point in time. A plain `copyfile` copies bytes without knowing anything about transactions: when it runs in the middle of someone's write, the file may contain half of a transaction, without the journal needed to undo it.

Example: a writer inserts 3,000 rows in an open transaction (some pages already written to the file) while the backup runs: the backup holds exactly the 100 committed rows; a file copy at that moment contains a mixture.

## Complexity

`O(database size)`.

## Another way

`VACUUM INTO 'backup.db'` also writes a consistent, compacted copy. For PostgreSQL the tools are `pg_dump` (logical) and base backups with the write-ahead log (physical).

## Why it matters

A backup you have not tested is a hope, not a backup. The next problem tests the restore.
