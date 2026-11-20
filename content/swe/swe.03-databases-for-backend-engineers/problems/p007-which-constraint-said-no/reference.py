import sqlite3

KINDS = ("UNIQUE", "NOT NULL", "CHECK", "FOREIGN KEY")


def attempt(db, sql):
    try:
        db.execute(sql)
    except sqlite3.IntegrityError as exc:
        for kind in KINDS:
            if kind in str(exc):
                return kind
        raise
    return "ok"
