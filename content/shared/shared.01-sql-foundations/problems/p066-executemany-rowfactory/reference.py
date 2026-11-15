import sqlite3
from contextlib import closing


def add_books(con, rows):
    with con:
        con.executemany("INSERT INTO books (title, category, price) VALUES (?, ?, ?)", rows)
    return len(rows)


def books_as_dicts(con, category):
    old = con.row_factory
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute("SELECT title, price FROM books WHERE category = ? ORDER BY title", (category,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        con.row_factory = old


def average_by_category(db_path):
    with closing(sqlite3.connect(db_path)) as con:
        cur = con.execute("SELECT category, ROUND(AVG(price), 2) FROM books GROUP BY category")
        return dict(cur.fetchall())
