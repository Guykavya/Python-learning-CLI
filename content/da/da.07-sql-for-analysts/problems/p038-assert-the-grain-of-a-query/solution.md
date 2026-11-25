## Approach

Run the query once to a DataFrame. Check for `NULL` keys first (a NULL key is never a valid identifier, and `duplicated` treats NULLs as equal, which would produce a confusing message). Then find duplicates with `duplicated(subset=key, keep=False)`, name up to three distinct duplicated keys in the message, and raise. If both checks pass, return the DataFrame so the caller can keep working with it.

## Code

```python
def assert_grain(con, sql, key):
    df = con.execute(sql).df()
    if df[key].isna().any().any():
        raise AssertionError(f"NULL values in key columns {key}: the grain is wrong")
    dup = df[df.duplicated(subset=key, keep=False)]
    if len(dup):
        examples = dup[key].drop_duplicates().head(3).values.tolist()
        raise AssertionError(f"{len(dup)} rows share duplicate keys, e.g. {examples}: the grain is wrong")
    return df
```

## Complexity

O(n) for the duplicate check.

## Another way

Do the check in SQL: `SELECT key, count(*) FROM (sql) GROUP BY key HAVING count(*) > 1 LIMIT 3` finds the offenders without loading the whole result. For huge results that is the better design; the pandas version is simplest for analysis-sized data.

## Pitfall to remember

A grain check proves "one row per key", not that the numbers are right. Pair it with a total check (the sum of the result equals the sum of the source).
