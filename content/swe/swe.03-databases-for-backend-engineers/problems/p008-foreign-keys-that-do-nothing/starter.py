import sqlite3


def connect(path=":memory:"):
    # BUG: foreign keys are off by default in SQLite
    return sqlite3.connect(path)
