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
