# Two engines, one answer

Chapter section 10.6. A strong habit: compute a metric in pandas **and** in SQL and compare. If they disagree, one of the
two has a bug in its logic, and the disagreement tells you where to look.

Write `both_ways(name, pandas_value, sql, con)`.

- `sql` is a text with one `SELECT` that returns **one number** (first column of the first row).
  `con` is an open `sqlite3` connection. Run the query with `con.execute(sql)`.
- Compare the SQL number with `pandas_value`. They **match** when `abs(pandas_value - sql_value) <= 0.005`.
- On a match, return the text `"<name>: pandas=<p> sql=<s> MATCH"`, where `<p>` and `<s>` are the values written with
  `f"{x:,.2f}"` (two decimals, thousands separator).
- On a difference **larger than 0.005**, raise `AssertionError` with the text
  `"<name>: MISMATCH pandas=<p> sql=<s>"` (same number format), so the message shows **both** numbers.
- If the SQL returns no row, or its number is `NULL` (`None`), raise `AssertionError` with
  `"<name>: MISMATCH pandas=<p> sql=None"`.

## Example

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE jobs (job_id INTEGER, created_at TEXT)")
con.executemany("INSERT INTO jobs VALUES (?, ?)", [(1, "2025-02-01 00:00:00"), (2, "2025-02-28 15:30:00"), (3, "2025-03-01 00:00:00")])
sql = "SELECT COUNT(*) FROM jobs WHERE created_at >= '2025-02-01' AND created_at < '2025-03-01'"
print(both_ways("jobs created in Feb", 2, sql, con))
try:
    both_ways("jobs created in Feb", 3, sql, con)
except AssertionError as e:
    print(e)
```

```text
jobs created in Feb: pandas=2.00 sql=2.00 MATCH
jobs created in Feb: MISMATCH pandas=3.00 sql=2.00
```
