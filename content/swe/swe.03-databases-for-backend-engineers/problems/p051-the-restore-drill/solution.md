## Approach

```python
import os
import sqlite3


class RestoreFailed(Exception):
    pass


def fingerprint(conn):
    result = {}
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for table in tables:
        numeric = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")') if r[2].upper() in ("INTEGER", "REAL")]
        sums = {c: conn.execute(f'SELECT COALESCE(SUM("{c}"), 0) FROM "{table}"').fetchone()[0] for c in numeric}
        result[table] = {"rows": conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0], "sums": sums}
    return result


def restore_and_verify(backup_path, expected, dest_path):
    if os.path.exists(dest_path):
        raise FileExistsError(dest_path)
    try:
        source = sqlite3.connect(backup_path)
        if source.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise RestoreFailed("the backup fails the integrity check")
        dest = sqlite3.connect(dest_path)
        source.backup(dest)
        source.close()
        actual = fingerprint(dest)
        dest.close()
    except sqlite3.DatabaseError as exc:
        raise RestoreFailed(f"the backup cannot be read: {exc}") from exc
    differences = sorted(t for t in set(expected) | set(actual) if expected.get(t) != actual.get(t))
    if differences:
        raise RestoreFailed("tables differ after the restore: " + ", ".join(differences))
    return actual
```

The **fingerprint** is a summary that changes when the data changes: counts catch missing or extra rows, sums catch changed numbers. It is not proof of identity (two different tables could have the same sums), but it is cheap, readable, and catches the usual failures: an empty table, a truncated file, a restore of the wrong day. `integrity_check` catches a damaged file. Restoring into a **new** file means the test cannot harm the live database, and the comparison names the tables that differ so that you know where to look. A truncated or garbage file raises `sqlite3.DatabaseError`, which is turned into `RestoreFailed`: **loudly**, never silently with fewer rows.

Example: if `orders` lost a row, the message is `tables differ after the restore: orders`.

## Complexity

`O(database size)`.

## Another way

For stronger checks, hash each table's rows in primary key order, or compare a few critical business queries (total revenue, last order id). Run the drill on a schedule, not once.

## Why it matters

The restore drill is the only evidence that your backups work. Many teams discover during an outage that the backup job had been writing empty files for months.
