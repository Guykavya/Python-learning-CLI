import hashlib
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from solution import backup, drill

T0 = 1_700_000_000                       # 2023-11-14 22:13:20 UTC


def make_db(path, orders=5, table="orders"):
    with closing(sqlite3.connect(path)) as db:
        db.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY, item TEXT, quantity INTEGER)")
        db.executemany(f"INSERT INTO {table} (item, quantity) VALUES (?, ?)", [(f"item-{i}", i) for i in range(orders)])
        db.commit()
    return Path(path)


def count_orders(path):
    with closing(sqlite3.connect(path)) as db:
        return db.execute("SELECT count(*) FROM orders").fetchone()[0]


def test_name_checksum_and_content(tmp_path):
    db = make_db(tmp_path / "pagebound.db", orders=7)
    path, digest = backup(db, tmp_path / "backups", now=lambda: T0)
    assert path == tmp_path / "backups" / "pagebound-20231114T221320Z.db", f"Name: <stem>-<UTC stamp>.db; got {path.name}"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, "The returned digest is the SHA-256 of the backup file."
    sidecar = Path(f"{path}.sha256").read_text(encoding="utf-8")
    assert sidecar == f"{digest}  {path.name}\n", f"The checksum file reads '<digest>  <file name>' plus a newline; got {sidecar!r}"
    assert count_orders(path) == 7, "The backup holds the data of the source."


def test_a_backup_dir_is_created(tmp_path):
    db = make_db(tmp_path / "a.db")
    backup(db, tmp_path / "deep" / "er" / "backups", now=lambda: T0)
    assert (tmp_path / "deep" / "er" / "backups").is_dir()


def test_the_source_is_not_modified(tmp_path):
    db = make_db(tmp_path / "pagebound.db")
    before = db.read_bytes()
    backup(db, tmp_path / "b", now=lambda: T0)
    assert db.read_bytes() == before, "A backup never changes the source (it is opened read-only)."


def test_data_in_the_wal_is_included(tmp_path):
    db = tmp_path / "live.db"
    writer = sqlite3.connect(db)
    writer.execute("PRAGMA journal_mode = WAL")
    writer.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, item TEXT)")
    writer.executemany("INSERT INTO orders (item) VALUES (?)", [("x",)] * 5)
    writer.commit()                                            # committed, but still in the write-ahead log: the app keeps the file open
    try:
        path, _ = backup(db, tmp_path / "b", now=lambda: T0)
    finally:
        writer.close()
    assert count_orders(path) == 5, "The online backup API sees committed rows that a plain file copy of the main file would miss."


def test_rotation_keeps_the_newest_with_their_checksums(tmp_path):
    db = make_db(tmp_path / "pagebound.db")
    names = []
    for day in range(5):
        path, _ = backup(db, tmp_path / "b", keep=3, now=lambda day=day: T0 + day * 86400)
        names.append(path.name)
    left = sorted(p.name for p in (tmp_path / "b").iterdir())
    assert left == sorted(names[2:] + [n + ".sha256" for n in names[2:]]), f"keep=3 leaves the 3 newest backups and their .sha256 files; got {left}"


def test_other_databases_are_not_touched(tmp_path):
    a, b = make_db(tmp_path / "pagebound.db"), make_db(tmp_path / "audit.db")
    for day in range(3):
        backup(b, tmp_path / "b", keep=7, now=lambda day=day: T0 + day * 86400)
    for day in range(4):
        backup(a, tmp_path / "b", keep=1, now=lambda day=day: T0 + day * 86400)
    audit = sorted(p.name for p in (tmp_path / "b").glob("audit-*.db"))
    assert len(audit) == 3, "Rotation of 'pagebound' backups must not delete the backups of 'audit' (match the stem + '-')."
    assert len(list((tmp_path / "b").glob("pagebound-*.db"))) == 1


def test_keep_must_be_positive(tmp_path):
    db = make_db(tmp_path / "a.db")
    with pytest.raises(ValueError):
        backup(db, tmp_path / "b", keep=0)


def test_a_broken_source_leaves_no_backup(tmp_path):
    bad = tmp_path / "broken.db"
    bad.write_bytes(b"this is not a sqlite database" * 100)
    with pytest.raises(RuntimeError, match="backup FAILED"):
        backup(bad, tmp_path / "b", now=lambda: T0)
    assert list((tmp_path / "b").iterdir()) == [], "A backup that failed must not be kept (and no checksum file either)."


def test_a_missing_source_fails_cleanly(tmp_path):
    with pytest.raises(RuntimeError, match="backup FAILED"):
        backup(tmp_path / "nothing.db", tmp_path / "b", now=lambda: T0)
    assert not (tmp_path / "nothing.db").exists(), "Opening the source read-only must not create an empty database."
    assert list((tmp_path / "b").iterdir()) == []


def test_drill_on_a_good_backup(tmp_path):
    path, _ = backup(make_db(tmp_path / "pagebound.db", orders=20), tmp_path / "b", now=lambda: T0)
    steps, count = drill(path, min_orders=20)
    assert steps == [("checksum matches", True), ("integrity check ok", True), ("table 'orders' exists", True), ("at least 20 order(s) present", True)], \
        f"Four steps, with exactly these names and in this order; got {steps}"
    assert count == 20


def test_drill_default_min_orders(tmp_path):
    path, _ = backup(make_db(tmp_path / "p.db", orders=1), tmp_path / "b", now=lambda: T0)
    assert drill(path)[0][3] == ("at least 1 order(s) present", True)


def test_drill_catches_too_few_orders(tmp_path):
    path, _ = backup(make_db(tmp_path / "p.db", orders=3), tmp_path / "b", now=lambda: T0)
    steps, count = drill(path, min_orders=10)
    assert steps[3] == ("at least 10 order(s) present", False) and count == 3 and all(ok for _, ok in steps[:3]), \
        "Only the last step fails: the backup is sound but holds less data than expected (an old or empty backup)."


def test_drill_catches_a_damaged_file(tmp_path):
    path, _ = backup(make_db(tmp_path / "p.db"), tmp_path / "b", now=lambda: T0)
    with path.open("ab") as f:
        f.write(b"garbage")
    steps, _ = drill(path)
    assert steps[0] == ("checksum matches", False), "A few corrupted bytes change the checksum: the drill must say so (chapter 13.2)."


def test_drill_on_a_file_that_is_not_a_database(tmp_path):
    junk = tmp_path / "junk.db"
    junk.write_bytes(b"not a database at all" * 50)
    Path(f"{junk}.sha256").write_text(f"{hashlib.sha256(junk.read_bytes()).hexdigest()}  junk.db\n", encoding="utf-8")
    steps, count = drill(junk)
    assert steps == [("checksum matches", True), ("integrity check ok", False), ("table 'orders' exists", False), ("at least 1 order(s) present", False)], \
        f"The checksum is right but nothing can be restored; got {steps}"
    assert count == 0


def test_drill_without_a_checksum_file(tmp_path):
    path, _ = backup(make_db(tmp_path / "p.db"), tmp_path / "b", now=lambda: T0)
    Path(f"{path}.sha256").unlink()
    steps, _ = drill(path)
    assert steps[0] == ("checksum matches", False), "A missing checksum file is a failed step, not an exception."


def test_drill_without_an_orders_table(tmp_path):
    path, _ = backup(make_db(tmp_path / "p.db", table="customers"), tmp_path / "b", now=lambda: T0)
    steps, count = drill(path)
    assert steps[1:] == [("integrity check ok", True), ("table 'orders' exists", False), ("at least 1 order(s) present", False)] and count == 0


def test_drill_of_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        drill(tmp_path / "nothing.db")
    assert not (tmp_path / "nothing.db").exists()
