def add_customer(con, name, city):
    cur = con.execute("INSERT INTO customers (name, city) VALUES (?, ?)", (name, city))
    con.commit()
    return cur.lastrowid


def find_customer(con, name):
    return con.execute(
        "SELECT customer_id, name, city FROM customers WHERE name = :name ORDER BY customer_id LIMIT 1",
        {"name": name},
    ).fetchone()


def books_between(con, low, high, category=None):
    rows = con.execute(
        """SELECT title FROM books
           WHERE price BETWEEN :low AND :high
             AND (:category IS NULL OR category = :category)
           ORDER BY price, title""",
        {"low": low, "high": high, "category": category},
    ).fetchall()
    return [title for (title,) in rows]
