## Approach

`fetchone()` returns the first row, or `None`. Take its first element, handle the "nothing" cases first (they cannot be
compared with a number), then compare with a tolerance: floats and `ROUND` make exact equality unreliable. Format both
numbers the same way so that two different numbers never look the same in the message.

## Code

```python
def both_ways(name, pandas_value, sql, con):
    row = con.execute(sql).fetchone()
    value = None if row is None else row[0]
    p = f"{float(pandas_value):,.2f}"
    if value is None:
        raise AssertionError(f"{name}: MISMATCH pandas={p} sql=None")
    s = f"{float(value):,.2f}"
    if abs(float(pandas_value) - float(value)) > 0.005:
        raise AssertionError(f"{name}: MISMATCH pandas={p} sql={s}")
    return f"{name}: pandas={p} sql={s} MATCH"
```

## Complexity

One query. The comparison is O(1).

## Another way

Return a small result object (`name`, `pandas`, `sql`, `ok`) and collect all checks in a list, so a report prints every
MATCH and MISMATCH at once instead of stopping at the first. `pytest.approx(pandas_value, abs=0.005)` is the same
tolerance in test code.
