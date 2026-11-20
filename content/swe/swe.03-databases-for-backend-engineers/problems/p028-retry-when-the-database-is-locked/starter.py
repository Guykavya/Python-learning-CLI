import sqlite3
import time


def run_in_transaction(connect, work, attempts=5, sleep=time.sleep):
    # TODO: retry only "database is locked" with backoff; roll back and close every attempt
    db = connect()
    result = work(db)
    db.commit()
    return result
