import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db
