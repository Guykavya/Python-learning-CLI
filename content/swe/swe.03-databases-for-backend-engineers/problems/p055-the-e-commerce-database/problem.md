# The e-commerce database

The project of chapter section 19: a small shop database with the checks you learned. Write everything in `solution.py`. The tests use a SQLite **file** in a temporary folder.

## Models (SQLAlchemy 2.x, `Base` and these exact names)

| Class (table) | Columns and constraints |
|---|---|
| `Customer` (`customers`) | `id`, `email` (unique), `name` |
| `Product` (`products`) | `id`, `sku` (unique), `name`, `price_paise` (**CHECK >= 0**), `stock` (**CHECK >= 0**), `version` (default 1) |
| `Order` (`orders`) | `id`, `customer_id` (foreign key), `total_paise` (default 0), `lines` (relationship, cascade `all, delete-orphan`) |
| `OrderLine` (`order_lines`) | `id`, `order_id` (foreign key), `product_id` (foreign key), `qty` (**CHECK > 0**), `unit_price_paise` (**CHECK >= 0**) |

Money is always **integer paise**. A line stores the price **at the time of the order** (`unit_price_paise`): changing a product's price later must not change old orders.

## Functions

- `make_engine(path)`: a SQLite engine for the file, with **`PRAGMA foreign_keys = ON` on every connection** (use the `connect` event), tables created.
- `seed(session)`: three customers (`Asha asha@x.com`, `Ravi ravi@x.com`, `Meena meena@x.com`) and five products (`sku, name, price_paise, stock`): `TEA, Green Tea, 25000, 10`; `COF, Coffee, 30000, 5`; `MUG, Mug, 45000, 3`; `BOOK, Notebook, 15000, 20`; `PEN, Pen, 500, 100`.
- `place_order(session, customer_id, items)`: `items` is a list of `(sku, qty)`. It **never oversells**: the stock check and the decrement are **one statement** (`UPDATE ... SET stock = stock - ?, version = version + 1 WHERE id = ? AND stock >= ?`, look at `rowcount`). It creates the order and its lines with the current prices, stores `total_paise`, **commits**, and returns the order id. All-or-nothing: if any item fails, nothing of the order stays (no order, no line, no stock change) and the session remains usable (use a savepoint, `begin_nested`). Errors: empty `items` or `qty <= 0` raise `ValueError`; unknown customer or sku raise `LookupError`; not enough stock raises `OutOfStock` (a subclass of `ValueError` that you define).
- `orders_with_totals(session)`: a list of `(order_id, customer_name, total_paise_computed_from_lines, number_of_lines)` ordered by order id, with **one SQL statement** (join and group by).
- `backup(src_path, dst_path)`, `fingerprint(conn)`, `restore_and_verify(backup_path, expected, dest_path)` and `RestoreFailed`: as in problems 50 and 51.

## What the tests check

Constraint violations (negative price or stock, quantity 0, duplicate e-mail or sku, an order for a missing customer even through raw SQL); orders keep their old prices; no overselling, **also when another session already took the stock** (your session still believes the stale `stock` it loaded earlier); all-or-nothing orders; `orders_with_totals` equals the stored totals and uses a single statement; the fingerprint after backup and restore equals the original.
