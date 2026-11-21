import hashlib
import sqlite3
import tempfile
import time
from contextlib import closing
from pathlib import Path


def backup(db_file, backup_dir, keep=7, now=time.time):
    if keep < 1:
        raise ValueError(f"keep must be at least 1, got {keep}")
    db_file, backup_dir = Path(db_file), Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(now()))
    target = backup_dir / f"{db_file.stem}-{stamp}.db"
    try:
        with closing(sqlite3.connect(f"{db_file.resolve().as_uri()}?mode=ro", uri=True)) as source, \
                closing(sqlite3.connect(target)) as copy:
            source.backup(copy)                                      # a consistent snapshot, even while the app writes
            verdict = copy.execute("PRAGMA integrity_check").fetchone()[0]
    except sqlite3.DatabaseError as exc:
        verdict = f"{type(exc).__name__}: {exc}"
    if verdict != "ok":
        target.unlink(missing_ok=True)                               # never keep a backup you already know is bad
        raise RuntimeError(f"backup FAILED: {verdict}")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    Path(f"{target}.sha256").write_text(f"{digest}  {target.name}\n", encoding="utf-8")
    for old in sorted(backup_dir.glob(f"{db_file.stem}-*.db"))[:-keep]:
        old.unlink()
        Path(f"{old}.sha256").unlink(missing_ok=True)
    return target, digest


def drill(backup_file, min_orders=1):
    backup_file = Path(backup_file)
    if not backup_file.is_file():
        raise FileNotFoundError(backup_file)
    steps = []
    try:
        expected = Path(f"{backup_file}.sha256").read_text(encoding="utf-8").split()[0]
        steps.append(("checksum matches", hashlib.sha256(backup_file.read_bytes()).hexdigest() == expected))
    except (OSError, IndexError):
        steps.append(("checksum matches", False))
    count, integrity, has_orders = 0, False, False
    with tempfile.TemporaryDirectory() as tmp:
        restored = Path(tmp) / "restored.db"
        try:
            with closing(sqlite3.connect(f"{backup_file.resolve().as_uri()}?mode=ro", uri=True)) as source, \
                    closing(sqlite3.connect(restored)) as target:
                source.backup(target)
                integrity = target.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
                tables = {row[0] for row in target.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
                has_orders = "orders" in tables
                count = target.execute("SELECT count(*) FROM orders").fetchone()[0] if has_orders else 0
        except sqlite3.DatabaseError:
            integrity, has_orders, count = False, False, 0
    steps += [("integrity check ok", integrity), ("table 'orders' exists", has_orders),
              (f"at least {min_orders} order(s) present", count >= min_orders)]
    return steps, count
