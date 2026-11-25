# Assert the grain of a query

Chapter section 10.1. A query that runs is not a query that is right. The most useful check is the **grain**: "this result has
exactly one row per user". After a `LEFT JOIN` from users to orders, the claim is false for every user who bought twice, and nothing
in SQL will tell you unless you test it.

Write

```python
def assert_grain(con, sql, key):
    ...
```

`con` is an open DuckDB connection, `sql` a query and `key` a **list of column names** that should identify one row. The
function runs the query and:

- raises `AssertionError` when any key column contains a **NULL** (the message must contain the word `NULL`);
- raises `AssertionError` when the same key appears in **more than one row** (the message must contain the word `duplicate`, in any
  case, and the key values of **up to 3** of the duplicated keys);
- otherwise **returns the result as a DataFrame**.

A key made of two columns is unique when the **pair** is unique, even if each column alone repeats.

```python
import duckdb
con = duckdb.connect()
df = assert_grain(con, "SELECT 1 AS id UNION ALL SELECT 2", ["id"])        # fine: returns a DataFrame with 2 rows
assert_grain(con, "SELECT 1 AS id UNION ALL SELECT 1", ["id"])             # AssertionError: ... duplicate ... 1
```

## Example

For `SELECT 'a' AS k, 1 AS v UNION ALL SELECT 'a', 2` with `key=["k"]` the message could be:
`1 duplicated key(s) in 2 rows, e.g. ('a',): the grain is wrong (duplicate keys)`.
