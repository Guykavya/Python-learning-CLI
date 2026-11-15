## Approach

Put each rule next to the column it protects. A `CHECK` passes when the condition is true **or unknown**, so `age >= 13` lets NULL through, which is what "optional" needs.

## Code

```python
SCRIPT = """
CREATE TABLE members (
  member_id INTEGER PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  name  TEXT NOT NULL,
  age   INTEGER CHECK (age >= 13),
  plan  TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro'))
);
"""
```

## Complexity

`UNIQUE` creates an index, so each insert pays an extra B-tree lookup (about O(log n)) in return for fast email lookups. Other constraints are checked in O(1) per row.

## Another way / portable SQL

You can write table-level constraints: `UNIQUE (email)`, `CHECK (plan IN (...))`. In SQLite, `INTEGER PRIMARY KEY` is an alias of the row id; in PostgreSQL use `GENERATED ALWAYS AS IDENTITY` and in MySQL `AUTO_INCREMENT`. Note: SQLite allows NULL in a non-integer PRIMARY KEY unless you add NOT NULL.
