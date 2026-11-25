## Hint 1

How do you get the first value of the first row of a query with `sqlite3`? What can it be when the table has no
matching rows (a missing row, or `NULL`)? Which comparison says "within half a cent", and which side of it is a mismatch?

## Hint 2

```text
row = con.execute(sql).fetchone()            # None when there is no row
value = row[0] if row else None
p = f"{pandas_value:,.2f}"
if value is None:                      raise AssertionError(f"{name}: MISMATCH pandas={p} sql=None")
s = f"{value:,.2f}"
if abs(pandas_value - value) > 0.005:  raise AssertionError(f"{name}: MISMATCH pandas={p} sql={s}")
return f"{name}: pandas={p} sql={s} MATCH"
```
