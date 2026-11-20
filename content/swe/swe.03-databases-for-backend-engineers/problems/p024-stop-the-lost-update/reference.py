import sqlite3


def buy(path, product_id):
    db = sqlite3.connect(path, timeout=10)
    try:
        with db:
            cur = db.execute("UPDATE products SET stock = stock - 1 WHERE id = ? AND stock > 0", (product_id,))
            if cur.rowcount == 0:
                return False
            db.execute("INSERT INTO sales(product_id) VALUES (?)", (product_id,))
            return True
    finally:
        db.close()
