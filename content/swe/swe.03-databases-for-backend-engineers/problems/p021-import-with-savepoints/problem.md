# Import with savepoints

Chapter section 6.5. A file of products is imported into

```sql
CREATE TABLE products (sku TEXT NOT NULL UNIQUE, qty INTEGER NOT NULL CHECK (qty > 0));
```

Some rows are bad (a duplicate `sku`, `qty = 0`, a missing value). One bad row must not stop the import, and the good rows must be committed **together, once, at the end**. Write

```python
import_rows(db, rows)       # rows: list of (sku, qty) tuples
```

- Put each row in its own **`SAVEPOINT`**. If the insert raises `sqlite3.IntegrityError`, roll back **to the savepoint** (only that row), remember `(line_number, error_text)` (lines count from 1) and go on.
- After the last row, commit **once**. Return the list of `(line, error_text)` for the bad rows (empty if all were good).
- Any **other** exception (for example `OperationalError: no such table`) rolls back the **whole** import (nothing is committed) and is re-raised.
- Start the transaction yourself with `BEGIN`, so that releasing a savepoint does not commit by accident.

## Example

```python
import_rows(db, [("a", 5), ("a", 2), ("b", 0), ("c", 7)])
# [(2, "UNIQUE constraint failed: products.sku"), (3, "CHECK constraint failed: qty > 0")]
# products now holds a (5) and c (7)
```
