# sqlite3 parameters: ? and :name

Never paste values into SQL text. Give the SQL **placeholders** and pass the values separately: the driver sends them as data, so quotes in a value cannot change the meaning of the query.

```python
con.execute("SELECT * FROM customers WHERE name = ?", (name,))          # positional: a tuple (note the comma)
con.execute("SELECT * FROM customers WHERE name = :name", {"name": name})   # named: a dict
```

The database has:

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT);
CREATE TABLE books (book_id INTEGER PRIMARY KEY, title TEXT, category TEXT, price REAL);
```

Write three functions in `solution.py`:

1. `add_customer(con, name, city)` inserts a customer (city may be `None`), commits, and returns the new `customer_id`.
2. `find_customer(con, name)` returns `(customer_id, name, city)` of the customer with exactly that name, or `None` if there is none. If several have it, return the one with the lowest id. Use a **named** parameter.
3. `books_between(con, low, high, category=None)` returns the list of titles with `low <= price <= high`, cheapest first (ties by title). If `category` is not `None`, only that category. Write it as one query with named parameters; pass `category` as a parameter, do not build different SQL strings.

No f-strings, `%` or `.format` in SQL (the test checks the source).

**Example**

```python
cid = add_customer(con, "O'Brien", None)      # an apostrophe in the value is fine with parameters
find_customer(con, "O'Brien")                 # (1, "O'Brien", None)
find_customer(con, "x' OR '1'='1")            # None  (it is just a name that does not exist)
```
