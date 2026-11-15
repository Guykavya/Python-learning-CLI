## Hint 1

Take the incidents one at a time.

Incident 1: what in the table definition tells SQLite that two rows with the same `id` are the
same order? What does `INSERT INTO orders VALUES (...)` do when the row is already there?

Incident 2: put your finger on the line that raised the `TypeError`. Which lines of the loop
had already run for page 2 at that moment, and which had not? What did the checkpoint file
say right after the crash, and what had been committed?

## Hint 2

Two changes, nothing else:

```
CREATE TABLE ... (id INTEGER PRIMARY KEY, ...)
INSERT INTO orders (...) VALUES (...)
ON CONFLICT (id) DO UPDATE SET status = excluded.status, amount = ..., qty = ..., updated_at = ...

loop:
    request page, raise_for_status, body
    rows = transform each order            # may crash: nothing saved yet
    with conn: write rows                  # may crash: rolled back, nothing saved yet
    page = body["next_page"]
    save_checkpoint({"next_page": page})   # only now is page k really done
```
