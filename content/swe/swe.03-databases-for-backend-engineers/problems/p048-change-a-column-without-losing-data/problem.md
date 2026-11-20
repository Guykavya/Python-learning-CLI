# Change a column without losing data

Chapter section 14. A table stores prices in **rupees as `REAL`**: `products(id, name, price REAL)`. Floats cannot hold money exactly, so the price must become **integer paise** (`price_paise INTEGER NOT NULL`), without losing a single price, and with the application running during the change.

One big "change the column" migration is dangerous (old code stops working at once). The safe pattern is **expand, migrate, contract**, in **three revisions**. Write six functions in `solution.py`:

| Revision | Functions | What it does |
|---|---|---|
| `0002` expand | `upgrade_0002`, `downgrade_0002` | add the nullable column `price_paise INTEGER`; downgrade drops it |
| `0003` migrate | `upgrade_0003`, `downgrade_0003` | **backfill** `price_paise = round(price * 100)` for every row where it is still `NULL`, **in batches** of at most 500 rows per `UPDATE`; downgrade sets `price_paise` back to `NULL` |
| `0004` contract | `upgrade_0004`, `downgrade_0004` | make `price_paise` `NOT NULL` and **drop** `price` (batch mode); downgrade adds `price REAL` back, makes `price_paise` nullable again, and fills `price = price_paise / 100.0` |

The tests (revision `0001` creates the table; `price` is nullable `REAL`):

- seed rows (`12.30`, `99.99`, `0.07`, `1000000.01`, `0.1`, ...) at revision 0001, then upgrade step by step;
- after `0002`, **a row written by the old code** (only `price`) must still be insertable;
- after `0003` every row has the exact integer (`12.30` is `1230`, `99.99` is `9999`, `0.07` is `7`), including the row written between the steps;
- after `0004` the column `price` is gone, `price_paise` is `NOT NULL`, no value changed;
- `downgrade` step by step brings back `price` with the original rupee values exactly (`12.3`, `99.99`, ...).
