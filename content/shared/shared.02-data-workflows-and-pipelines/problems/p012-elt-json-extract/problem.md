# ELT in SQLite: raw JSON in, clean table out

In ELT you **load first**: every order goes into a raw table exactly as the API sent it, as
JSON text. Then the transformation runs **inside the database**, in SQL. If the rules change
next month, you rebuild the clean table from the raw table without calling the API again.

SQLite can read JSON text with `json_extract(text, '$.customer.city')` (JSON `null` becomes SQL
`NULL`), check it with `json_valid(text)` (1 or 0) and count an array with
`json_array_length(text, '$.items')`.

Write two functions. Both take an open `sqlite3.Connection` and commit their work.

```python
def load_raw(conn, payloads, loaded_at):
```

- Create the table if it does not exist:
  `raw_orders(raw_id INTEGER PRIMARY KEY, loaded_at TEXT NOT NULL, payload TEXT NOT NULL)`.
- Insert one row per string in `payloads` (each string is the JSON text of one order), with the
  given `loaded_at` text. Store the text **exactly as received**: do not parse and re-dump it,
  and keep payloads that are not even valid JSON (the raw layer is the evidence of what arrived).
- Use `?` parameters, never string formatting (cities like `O'Brien Nagar` exist).
- Return the number of rows inserted. Calling it again appends more rows.

```python
def build_clean(conn):
```

- Drop `clean_orders` if it exists, then create it with **one** `CREATE TABLE clean_orders AS SELECT ...`
  statement over `raw_orders`. Columns, in this order:

| column | value |
|---|---|
| `id` | `$.id` as an integer |
| `email` | `$.customer.email`, trimmed and lower-cased |
| `city` | `$.customer.city`, trimmed; `NULL` if it is null or blank |
| `status` | `$.status`, trimmed and lower-cased |
| `amount_cents` | `$.amount` (a string like `"19.99"`) as whole cents, an integer: `1999` |
| `currency` | `$.currency`, upper-cased |
| `created_at` | `$.created_at`, unchanged text |
| `item_count` | the number of elements in `$.items` |

- Skip raw rows whose payload is not valid JSON (otherwise `json_extract` raises "malformed JSON").
- Return the number of rows in `clean_orders`.

Running `build_clean` twice must give the same table. (If the same order was loaded twice, the
clean table has it twice. Removing duplicates is a later topic in this module.)

**Careful with cents.** `19.99 * 100` in floating point is `1998.9999999999998`, and
`CAST(... AS INTEGER)` cuts that to `1998`. Round before you cast.

**Example**

```python
load_raw(conn, ['{"id": 101, "customer": {"email": " Asha@Example.com", "city": "Pune"}, '
                '"status": "Shipped", "amount": "19.99", "currency": "inr", '
                '"created_at": "2024-06-01T10:00:00Z", "updated_at": "2024-06-01T12:00:00Z", '
                '"items": [{"sku": "B1", "qty": 2}]}',
                '{"id": 102, broken'], "2024-06-02T01:00:00Z")      # -> 2
build_clean(conn)                                                       # -> 1
conn.execute("SELECT * FROM clean_orders").fetchall()
# [(101, 'asha@example.com', 'Pune', 'shipped', 1999, 'INR', '2024-06-01T10:00:00Z', 1)]
```
