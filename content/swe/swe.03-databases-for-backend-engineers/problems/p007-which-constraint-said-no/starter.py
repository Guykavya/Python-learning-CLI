import sqlite3


def attempt(db, sql):
    # TODO: run the statement; map IntegrityError messages to UNIQUE / NOT NULL / CHECK / FOREIGN KEY
    db.execute(sql)
    return "ok"
