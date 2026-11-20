import sqlite3
import time


def buy(path, product_id):
    db = sqlite3.connect(path, timeout=10)
    try:
        stock = db.execute("SELECT stock FROM products WHERE id = ?", (product_id,)).fetchone()[0]
        if stock <= 0:
            return False
        time.sleep(0.0005)                      # "a little work" between the read and the write
        db.execute("UPDATE products SET stock = ? WHERE id = ?", (stock - 1, product_id))
        db.execute("INSERT INTO sales(product_id) VALUES (?)", (product_id,))
        db.commit()
        return True
    finally:
        db.close()
