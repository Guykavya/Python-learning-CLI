import sqlite3


def import_rows(db, rows):
    # TODO: BEGIN; per row SAVEPOINT / INSERT / ROLLBACK TO on IntegrityError / RELEASE; commit once
    for sku, qty in rows:
        db.execute("INSERT INTO products(sku, qty) VALUES (?, ?)", (sku, qty))
    db.commit()
    return []
