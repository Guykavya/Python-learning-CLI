# Trace: what each role can see

**Least privilege** means every person or program gets access to exactly the data it needs for
its job and nothing more. SQLite has no users or `GRANT`, so a small pipeline often does it in two
layers:

1. **Views** shape the data per role: a view is a saved `SELECT`, so it can leave out columns,
   mask them or filter rows. A view stores no data; it runs its query on the live table each time.
2. An **allow-list** in the application decides which views each role may query at all.

Work out, line by line, exactly what this program prints. Write one line per `print` call, with
the same spacing and quotes that `print` would give. The program needs no input. Two reminders:
`cursor.description` gives one tuple per result column, whose first item is the column name
(the alias if there is one, otherwise the expression text exactly as written), and in SQL
`substr(text, start)` counts from 1 and `instr(text, '@')` is the 1-based position of `@`.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.executescript("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY, email TEXT, customer_key TEXT,
    city TEXT, status TEXT, amount_cents INTEGER
);
INSERT INTO orders VALUES
    (101, 'asha@example.com', 'k1', 'Pune', 'shipped', 1999),
    (102, 'ravi@example.com', 'k2', NULL, 'pending', 25000),
    (103, 'asha@example.com', 'k1', 'Pune', 'cancelled', 500);

CREATE VIEW support_orders AS
    SELECT id, status, city,
           substr(email, 1, 1) || '***@' || substr(email, instr(email, '@') + 1) AS email
    FROM orders;
CREATE VIEW analyst_orders AS
    SELECT id, customer_key, city, status, amount_cents FROM orders
    WHERE status != 'cancelled';
""")

GRANTS = {
    "support": {"support_orders"},
    "analyst": {"analyst_orders"},
    "admin": {"orders", "support_orders", "analyst_orders"},
}


def query(role, view, columns="*", rest="ORDER BY id"):
    if view not in GRANTS.get(role, set()):
        return f"DENIED {role} -> {view}"
    sql = f"SELECT {columns} FROM {view} {rest}"
    try:
        cursor = conn.execute(sql)
    except sqlite3.OperationalError as error:
        return f"ERROR {error}"
    names = [d[0] for d in cursor.description]
    return names, cursor.fetchall()


print(query("support", "support_orders", rest="WHERE id = 101"))
print(query("support", "orders"))
print(query("support", "support_orders", columns="id, amount_cents"))
print(query("analyst", "analyst_orders", columns="customer_key, COUNT(*) AS n",
            rest="GROUP BY customer_key ORDER BY customer_key"))
print(query("analyst", "analyst_orders", columns="id, city"))
print(query("intern", "analyst_orders"))
conn.execute("UPDATE orders SET status = 'shipped' WHERE id = 103")
print(query("analyst", "analyst_orders", columns="SUM(amount_cents)", rest=""))
print(query("admin", "orders", columns="COUNT(DISTINCT email), COUNT(DISTINCT customer_key)",
            rest=""))
try:
    conn.execute("DELETE FROM support_orders WHERE id = 101")
except sqlite3.OperationalError as error:
    print("ERROR", error)
print(query("admin", "support_orders", columns="COUNT(*)", rest=""))
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE t (a INTEGER, b TEXT)")
conn.execute("INSERT INTO t VALUES (1, 'x')")
conn.execute("CREATE VIEW v AS SELECT a AS first FROM t")
cursor = conn.execute("SELECT * FROM v")
print([d[0] for d in cursor.description], cursor.fetchall())
```

prints

```
['first'] [(1,)]
```
