import sqlite3


def import_rows(db, rows):
    errors = []
    db.execute("BEGIN")
    try:
        for line, (sku, qty) in enumerate(rows, 1):
            db.execute("SAVEPOINT row")
            try:
                db.execute("INSERT INTO products(sku, qty) VALUES (?, ?)", (sku, qty))
            except sqlite3.IntegrityError as exc:
                db.execute("ROLLBACK TO row")
                errors.append((line, str(exc)))
            db.execute("RELEASE row")
    except BaseException:
        db.rollback()
        raise
    db.commit()
    return errors
