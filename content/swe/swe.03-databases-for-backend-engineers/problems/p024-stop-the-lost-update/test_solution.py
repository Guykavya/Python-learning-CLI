import sqlite3


def connect(path=":memory:"):
    db = sqlite3.connect(path, timeout=5)
    db.execute("PRAGMA foreign_keys = ON")
    return db


def plan(db, sql, params=()):
    return [row[3] for row in db.execute("EXPLAIN QUERY PLAN " + sql, params)]



import threading

from solution import buy


def setup(path, stock):
    db = connect(path)
    db.executescript(f"""
        CREATE TABLE products (id INTEGER PRIMARY KEY, stock INTEGER NOT NULL CHECK (stock >= 0));
        CREATE TABLE sales (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER NOT NULL);
        INSERT INTO products VALUES (1, {stock});
    """)
    db.commit()
    db.close()


def run_threads(path, threads, each):
    results = []
    lock = threading.Lock()

    def worker():
        mine = [buy(path, 1) for _ in range(each)]
        with lock:
            results.extend(mine)

    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=60)
    return results


def test_single_buyer(tmp_path):
    path = str(tmp_path / "s.db")
    setup(path, 2)
    assert [buy(path, 1) for _ in range(3)] == [True, True, False]


def test_eight_threads_never_lose_a_sale(tmp_path):
    path = str(tmp_path / "s.db")
    setup(path, 100)
    results = run_threads(path, 8, 20)             # 160 attempts for 100 items
    db = connect(path)
    stock = db.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
    sales = db.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    assert len(results) == 160, "Every thread must finish."
    assert results.count(True) == 100, (
        f"{results.count(True)} buys returned True, but exactly 100 items existed. Do the check and the change in ONE UPDATE.")
    assert stock == 0, f"Final stock is {stock}; it must be 0 (a lost update leaves stock behind)."
    assert sales == 100, f"{sales} rows in sales; there must be one per successful buy (100)."


def test_never_below_zero_and_counts_agree(tmp_path):
    path = str(tmp_path / "s.db")
    setup(path, 30)
    results = run_threads(path, 6, 10)             # 60 attempts for 30 items
    db = connect(path)
    stock = db.execute("SELECT stock FROM products WHERE id = 1").fetchone()[0]
    assert stock >= 0 and results.count(True) == 30 - stock == db.execute("SELECT COUNT(*) FROM sales").fetchone()[0]


def test_fewer_attempts_than_stock(tmp_path):
    path = str(tmp_path / "s.db")
    setup(path, 100)
    results = run_threads(path, 4, 10)
    assert results.count(True) == 40 and all(results)
    assert connect(path).execute("SELECT stock FROM products").fetchone()[0] == 60
