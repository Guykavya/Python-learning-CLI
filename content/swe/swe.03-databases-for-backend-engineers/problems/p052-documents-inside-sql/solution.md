## Approach

```python
def find_by_attr(db, key, value):
    if value is None or not isinstance(value, (str, int, float, bool)):
        raise ValueError("value must be a string, number or boolean")
    rows = db.execute(
        "SELECT DISTINCT p.id FROM products p, json_each(p.attrs) j WHERE j.key = ? AND j.value = ? ORDER BY p.id",
        (key, value))
    return [r[0] for r in rows]
```

`json_each(attrs)` turns the top-level members of the JSON object into **rows** with the columns `key` and `value`. `j.key = ?` compares the key as ordinary text, so dots, spaces and quotes in a key mean exactly themselves (a JSON *path* such as `$."5\" screen"` cannot even express a key that contains a double quote). `j.value` is a SQL value of the right type (text, integer, real; JSON `true` becomes `1`), so comparing with a bound Python value works for strings, numbers and booleans. A product without the key produces no matching row. `None` is refused because JSON `null` and a missing key would be indistinguishable here.

Example: `find_by_attr(db, "size", "M")` finds the rows of `json_each` with `key = 'size'` and `value = 'M'`.

## Complexity

A scan of all products and their keys. For one fixed key, an expression index on `json_extract(attrs, '$.color')` (problem 16) makes it a search.

## Another way

PostgreSQL has `jsonb` with `@>` containment and GIN indexes; MongoDB is a database built on documents. In SQLite, JSON columns are a pragmatic middle way, not a replacement for proper columns.

## Why it matters

Flexible attributes are convenient, but values in JSON have no constraints, types or foreign keys. Use them for truly variable data, not to avoid designing a schema.
