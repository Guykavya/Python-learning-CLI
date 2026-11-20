import sqlite3
import time


def run_in_transaction(connect, work, attempts=5, sleep=time.sleep):
    for attempt in range(attempts):
        db = connect()
        try:
            result = work(db)
            db.commit()
        except sqlite3.OperationalError as exc:
            db.rollback()
            if "database is locked" not in str(exc) or attempt == attempts - 1:
                raise
            sleep(0.05 * 2 ** attempt)
        except BaseException:
            db.rollback()
            raise
        else:
            return result
        finally:
            db.close()
