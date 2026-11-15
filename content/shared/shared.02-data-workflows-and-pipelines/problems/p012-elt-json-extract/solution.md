## Approach

**Load.** The raw table has three columns: a surrogate key, when the row arrived, and the
payload text. `executemany` with `?` parameters inserts the list, and quotes inside the text
cannot break the SQL. The text is not parsed: parsing and re-dumping would change spacing and
key order, and would crash on the very payloads you most need to keep as evidence.

**Transform.** The whole clean layer is one `SELECT` over the raw table:

- `json_extract(payload, '$.customer.city')` walks into the nested object; JSON `null` comes
  back as SQL `NULL`, and SQL functions such as `trim` and `lower` pass `NULL` through.
- `NULLIF(trim(...), '')` turns a blank city into `NULL`, so a null check finds it.
- Money becomes integer cents, because SQLite has no exact decimal type. The amount text is cast
  to `REAL`, multiplied by 100, **rounded**, then cast to `INTEGER`. Without `ROUND`, values such
  as `19.99` (really `1998.9999999999998` after the multiplication) lose a cent.
- `WHERE json_valid(payload)` keeps the broken payloads out; they stay in `raw_orders` for
  someone to inspect.

`DROP TABLE IF EXISTS` + `CREATE TABLE ... AS SELECT` makes the build **repeatable**: it does not
matter how often it runs, the clean table is always "the current rules applied to all raw rows".
That is the main benefit of ELT. When the analysts change a rule, you change this one statement
and rebuild; the API is never called again.

## Code

```python
import sqlite3

CREATE_RAW = """
CREATE TABLE IF NOT EXISTS raw_orders (
    raw_id    INTEGER PRIMARY KEY,
    loaded_at TEXT NOT NULL,
    payload   TEXT NOT NULL
)
"""

BUILD_CLEAN = """
CREATE TABLE clean_orders AS
SELECT
    CAST(json_extract(payload, '$.id') AS INTEGER)                          AS id,
    lower(trim(json_extract(payload, '$.customer.email')))                  AS email,
    NULLIF(trim(json_extract(payload, '$.customer.city')), '')              AS city,
    lower(trim(json_extract(payload, '$.status')))                          AS status,
    CAST(ROUND(CAST(json_extract(payload, '$.amount') AS REAL) * 100) AS INTEGER) AS amount_cents,
    upper(json_extract(payload, '$.currency'))                              AS currency,
    json_extract(payload, '$.created_at')                                   AS created_at,
    json_array_length(payload, '$.items')                                   AS item_count
FROM raw_orders
WHERE json_valid(payload)
"""


def load_raw(conn, payloads, loaded_at):
    conn.execute(CREATE_RAW)
    rows = [(loaded_at, text) for text in payloads]
    conn.executemany("INSERT INTO raw_orders (loaded_at, payload) VALUES (?, ?)", rows)
    conn.commit()
    return len(rows)


def build_clean(conn):
    conn.execute("DROP TABLE IF EXISTS clean_orders")
    conn.execute(BUILD_CLEAN)
    conn.commit()
    return conn.execute("SELECT COUNT(*) FROM clean_orders").fetchone()[0]
```

## Complexity

The load is O(n) inserts. The build reads every raw row once and parses its JSON: O(total
payload size). For very large raw tables you would rebuild only the new part (an incremental
build, later in this module).

## Another way

Instead of a table, make the clean layer a **view**:
`CREATE VIEW clean_orders AS SELECT ... FROM raw_orders WHERE json_valid(payload)`. It is always
up to date and costs no storage, but the JSON is parsed again on every query. A table is a
snapshot that is fast to query; a view is a saved query. Many ELT setups use views for
staging and tables for the final, heavily-queried layer. The amount could also be converted
without floating point, by splitting the text at the dot with `instr` and `substr`.
