# A contact book on `sqlite3` with parameters

`sqlite3` is a complete SQL database in the standard library. The whole database is one file (or
lives only in memory with `":memory:"`), and there is no server to install.

Three habits make `sqlite3` code correct:

1. **Parameters, never string formatting.** Write `?` in the SQL and pass the values separately:
   `conn.execute("SELECT * FROM t WHERE name = ?", (name,))`. The database receives the value as data,
   so a name like `O'Brien` works and a name like `x'); DROP TABLE t; --` is just a strange name.
2. **Commit.** Changes (`INSERT`, `UPDATE`, `DELETE`) are inside a transaction until you call
   `conn.commit()` (or leave a `with conn:` block without an error). Close without committing and the
   changes are gone.
3. **Close** the connection when you are done (on Windows an open database file cannot be deleted).

`conn.row_factory = sqlite3.Row` makes rows behave like dicts: `row["name"]`, and `dict(row)`.

## Your task

Write a class `ContactBook` in `solution.py`:

| Method | Behaviour |
|---|---|
| `ContactBook(path=":memory:")` | Connect and create the table if it does not exist: `contacts(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, city TEXT)`. |
| `add(name, email, city=None) -> int` | Insert; return the new `id` (`cursor.lastrowid`). An email that already exists raises `ValueError`. |
| `get(contact_id) -> dict \| None` | `{"id", "name", "email", "city"}` or `None` if there is no such id. |
| `find_by_city(city) -> list[dict]` | All contacts in that city, ordered by name. |
| `update_email(contact_id, email) -> bool` | `True` if a row was changed, `False` if the id does not exist. A duplicate email raises `ValueError`. |
| `delete(contact_id) -> bool` | `True` if a row was deleted. |
| `count() -> int` | Number of contacts. |
| `close()` | Close the connection. |
| `with ContactBook(path) as book:` | `__enter__` returns the book, `__exit__` closes it. |

Every method that changes data must **commit**, so the data is still there after closing and opening
the file again. Use `?` parameters for every value.

**Example**

```python
with ContactBook("contacts.db") as book:
    a = book.add("Asha", "asha@example.com", "Pune")      # 1
    book.add("Ravi", "ravi@example.com", "Pune")          # 2
    book.add("O'Brien", "ob@example.com")                 # 3   the quote is no problem
    book.find_by_city("Pune")
    # [{'id': 1, 'name': 'Asha', 'email': 'asha@example.com', 'city': 'Pune'},
    #  {'id': 2, 'name': 'Ravi', 'email': 'ravi@example.com', 'city': 'Pune'}]
    book.add("Copy", "asha@example.com")                  # ValueError: email already used

with ContactBook("contacts.db") as book:
    book.count()                                          # 3    the data was committed
```
