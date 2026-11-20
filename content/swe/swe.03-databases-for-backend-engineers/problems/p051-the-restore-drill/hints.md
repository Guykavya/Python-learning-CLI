## Hint 1

What does "the data is the same" mean in a way that is cheap to compute? Count the rows of every table, and add up the numeric columns: a lost or changed row changes at least one of the numbers.

## Hint 2

`SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'` lists the tables; `PRAGMA table_info("t")` gives the columns with their declared types. Table names cannot be bound parameters: quote them with double quotes.

## Hint 3

```text
fingerprint: for each table: rows = COUNT(*); sums = {col: COALESCE(SUM(col), 0)} for INTEGER/REAL columns
restore_and_verify: FileExistsError; try: open backup, integrity_check != ok -> RestoreFailed; backup() into dest; fingerprint(dest)
                    except sqlite3.DatabaseError -> RestoreFailed
differences = sorted tables where expected.get(t) != actual.get(t) ; raise RestoreFailed("... " + ", ".join(differences))
```
