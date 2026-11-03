import sqlite3
import pytest

from solution import SCRIPT

A = """CREATE TABLE orders_flat (order_id INTEGER, customer_name TEXT, customer_city TEXT, book_title TEXT, book_price REAL, qty INTEGER);
INSERT INTO orders_flat VALUES
 (1,'Ada','Pune','Rust Basics',30,1),(1,'Ada','Pune','Go Tour',20,2),(2,'Bo','Oslo','Rust Basics',30,1),(3,'Ada','Pune','Go Tour',20,1);"""
B = """CREATE TABLE orders_flat (order_id INTEGER, customer_name TEXT, customer_city TEXT, book_title TEXT, book_price REAL, qty INTEGER);
INSERT INTO orders_flat VALUES
 (10,'Di',NULL,'Atlas',40,1),(10,'Di',NULL,'Tales',10,3),(11,'Eve','Rome','Atlas',40,2),(12,'Di',NULL,'Atlas',40,1),(13,'Fay','Rome','Tales',10,1);"""


def run(schema):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    try:
        con.executescript(SCRIPT)
    except sqlite3.Error as e:
        pytest.fail(f"SQLite rejected your script: {e}")
    return con


def cols(con, table):
    return [r[1] for r in con.execute(f"PRAGMA table_info({table})")]


@pytest.mark.parametrize("schema", [A, B])
def test_table_shapes(schema):
    con = run(schema)
    assert cols(con, "customers") == ["customer_id", "name", "city"], "customers needs columns customer_id, name, city (in that order)."
    assert cols(con, "books") == ["book_id", "title", "price"], "books needs columns book_id, title, price (in that order)."
    assert cols(con, "lines") == ["line_id", "order_id", "customer_id", "book_id", "qty"], "lines needs columns line_id, order_id, customer_id, book_id, qty."
    pk = {t: [r[1] for r in con.execute(f"PRAGMA table_info({t})") if r[5]] for t in ("customers", "books", "lines")}
    assert pk == {"customers": ["customer_id"], "books": ["book_id"], "lines": ["line_id"]}, f"Each table needs its id as PRIMARY KEY: {pk}"


@pytest.mark.parametrize("schema", [A, B])
def test_foreign_keys_declared(schema):
    con = run(schema)
    fks = {(r[2], r[3]) for r in con.execute("PRAGMA foreign_key_list(lines)")}
    assert fks == {("customers", "customer_id"), ("books", "book_id")}, f"lines must reference customers(customer_id) and books(book_id). Found {fks}."


@pytest.mark.parametrize("schema", [A, B])
def test_one_row_per_entity(schema):
    con = run(schema)
    flat = con.execute("SELECT COUNT(DISTINCT customer_name), COUNT(DISTINCT book_title), COUNT(*) FROM orders_flat").fetchone()
    got = (con.execute("SELECT COUNT(*) FROM customers").fetchone()[0], con.execute("SELECT COUNT(*) FROM books").fetchone()[0],
           con.execute("SELECT COUNT(*) FROM lines").fetchone()[0])
    assert got == flat, f"Expected (customers, books, lines) = {flat}, got {got}. One row per distinct customer, per distinct title, per flat row."


@pytest.mark.parametrize("schema", [A, B])
def test_join_back_gives_the_flat_rows(schema):
    con = run(schema)
    back = sorted(con.execute("""SELECT l.order_id, c.name, c.city, b.title, b.price, l.qty
                                 FROM lines l JOIN customers c ON c.customer_id = l.customer_id
                                              JOIN books b ON b.book_id = l.book_id""").fetchall(), key=repr)
    flat = sorted(con.execute("SELECT order_id, customer_name, customer_city, book_title, book_price, qty FROM orders_flat").fetchall(), key=repr)
    assert back == flat, "Joining lines, customers and books must give back exactly the flat rows. Check that you fetched the ids with a join, and that NULL cities survived."


def test_unique_names_enforced():
    con = run(A)
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO customers (name, city) VALUES ('Ada', 'Elsewhere')")
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO books (title, price) VALUES ('Go Tour', 1)")


def test_flat_table_kept():
    con = run(A)
    assert con.execute("SELECT COUNT(*) FROM orders_flat").fetchone()[0] == 4, "Leave orders_flat in place."
